from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .audit_log import log_audit
from .auth_utils import user_payload
from .serializers import SelfProfileSerializer


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):
    if request.method == "GET":
        return Response(user_payload(request.user))

    ser = SelfProfileSerializer(
        data=request.data,
        partial=True,
        context={"request": request},
    )
    ser.is_valid(raise_exception=True)
    if not ser.validated_data:
        return Response(
            {"detail": "No valid fields to update."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    ser.update(request.user, ser.validated_data)
    log_audit(
        request.user,
        "profile.update",
        resource_type="user",
        resource_id=request.user.pk,
        summary=f"Profile updated for {request.user.username}",
        metadata={"username": request.user.username},
    )
    return Response(user_payload(request.user))
