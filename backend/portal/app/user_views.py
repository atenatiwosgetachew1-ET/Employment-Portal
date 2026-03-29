from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from .audit_log import log_audit
from .auth_utils import (
    can_manage_all_users,
    can_manage_users,
    get_profile_role,
)
from .models import Notification, Profile
from .platform_views import UserPagination
from .serializers import UserCreateSerializer, UserListSerializer, UserUpdateSerializer


class IsSuperadminOrAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and can_manage_users(user))


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    pagination_class = UserPagination
    queryset = User.objects.all().select_related("profile").order_by("id")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = get_profile_role(self.request.user)
        if can_manage_all_users(self.request.user):
            queryset = qs
        elif can_manage_users(self.request.user):
            queryset = qs.filter(
                profile__role__in=[Profile.ROLE_STAFF, Profile.ROLE_CUSTOMER]
            )
        else:
            return qs.none()

        search = (self.request.query_params.get("q") or "").strip()
        role_filter = (self.request.query_params.get("role") or "").strip()
        is_active = (self.request.query_params.get("is_active") or "").strip().lower()

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(profile__phone__icontains=search)
            )

        if role_filter in {choice for choice, _ in Profile.ROLE_CHOICES}:
            queryset = queryset.filter(profile__role=role_filter)

        if is_active in {"true", "false"}:
            queryset = queryset.filter(is_active=(is_active == "true"))

        return queryset

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit(
            self.request.user,
            "user.create",
            resource_type="user",
            resource_id=user.pk,
            summary=f"Created user {user.username}",
            metadata={"username": user.username},
        )
        Notification.objects.create(
            user=user,
            title="Welcome",
            body=(
                f'Your account "{user.username}" is ready. '
                "You can sign in with the credentials you were given."
            ),
            kind=Notification.KIND_SUCCESS,
        )


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    queryset = User.objects.all().select_related("profile")
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return UserUpdateSerializer
        return UserListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if can_manage_all_users(self.request.user):
            return qs
        if can_manage_users(self.request.user):
            return qs.filter(profile__role__in=[Profile.ROLE_STAFF, Profile.ROLE_CUSTOMER])
        return qs.none()

    def perform_update(self, serializer):
        instance = serializer.save()
        log_audit(
            self.request.user,
            "user.update",
            resource_type="user",
            resource_id=instance.pk,
            summary=f"Updated user {instance.username}",
            metadata={"username": instance.username},
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pk == request.user.pk:
            return Response(
                {"detail": "You cannot delete your own account."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not can_manage_all_users(request.user):
            target_role = get_profile_role(instance)
            if target_role not in (Profile.ROLE_STAFF, Profile.ROLE_CUSTOMER):
                return Response(
                    {"detail": "You do not have permission to delete this account."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, instance):
        log_audit(
            self.request.user,
            "user.delete",
            resource_type="user",
            resource_id=instance.pk,
            summary=f"Deleted user {instance.username}",
            metadata={"username": instance.username},
        )
        instance.delete()
