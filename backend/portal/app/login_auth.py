from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .audit_log import log_audit
from .auth_utils import feature_enabled, user_payload
from .models import PlatformSettings, Profile
from .email_service import send_password_reset_email, send_verification_email
from .verification_code import generate_code, store_code_on_profile


def _max_failed_login_attempts():
    configured = getattr(settings, "LOGIN_MAX_FAILED_ATTEMPTS", 5)
    try:
        if platform_settings := PlatformSettings.objects.filter(pk=1).first():
            configured = platform_settings.login_max_failed_attempts
    except Exception:
        pass
    return max(1, int(configured))


def _login_lockout_minutes():
    configured = getattr(settings, "LOGIN_LOCKOUT_MINUTES", 15)
    try:
        if platform_settings := PlatformSettings.objects.filter(pk=1).first():
            configured = platform_settings.login_lockout_minutes
    except Exception:
        pass
    return max(1, int(configured))


def _lockout_message():
    return (
        f"Too many failed login attempts. Try again in {_login_lockout_minutes()} minutes. "
        "We also sent recovery instructions to your email if the account exists."
    )


def _send_login_recovery_email(user, profile):
    if not user.email:
        return
    if not profile.email_verified:
        plain = generate_code()
        store_code_on_profile(profile, plain)
        send_verification_email(user, plain)
        return
    send_password_reset_email(user)


def _record_failed_login_attempt(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"role": Profile.ROLE_CUSTOMER},
    )
    now = timezone.now()
    if profile.login_locked_until and profile.login_locked_until > now:
        return profile, True

    if profile.login_locked_until and profile.login_locked_until <= now:
        profile.failed_login_attempts = 0
        profile.login_locked_until = None

    profile.failed_login_attempts += 1
    should_lock = profile.failed_login_attempts >= _max_failed_login_attempts()
    if should_lock:
        profile.login_locked_until = now + timedelta(minutes=_login_lockout_minutes())
    profile.save(update_fields=["failed_login_attempts", "login_locked_until"])

    if should_lock:
        try:
            _send_login_recovery_email(user, profile)
        except Exception:
            pass
        log_audit(
            user,
            "auth.login_locked",
            resource_type="user",
            resource_id=user.pk,
            summary=f"Login temporarily locked for {user.username}",
            metadata={"username": user.username},
        )
    return profile, should_lock


def _clear_failed_login_attempts(profile):
    if profile.failed_login_attempts or profile.login_locked_until:
        profile.failed_login_attempts = 0
        profile.login_locked_until = None
        profile.save(update_fields=["failed_login_attempts", "login_locked_until"])


@csrf_protect
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login(request):
    if not feature_enabled("email_password_login_enabled"):
        return Response(
            {"success": False, "message": "Email/password login is currently disabled."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    username = (request.data.get("username") or "").strip()
    password = request.data.get("password")

    existing_user = None
    if username:
        existing_user = (
            User.objects.filter(username__iexact=username).select_related("profile").first()
        )
        if existing_user:
            profile = existing_user.profile
            now = timezone.now()
            if profile.login_locked_until and profile.login_locked_until > now:
                return Response(
                    {"success": False, "message": _lockout_message()},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

    user = authenticate(username=username, password=password)

    if user:
        profile, _ = Profile.objects.get_or_create(
            user=user,
            defaults={"role": Profile.ROLE_CUSTOMER},
        )
        if not profile.email_verified and not user.is_superuser:
            return Response(
                {
                    "success": False,
                    "message": "Please verify your email before signing in.",
                },
                status=403,
            )
        if not user.is_active:
            return Response(
                {"success": False, "message": "This account is inactive."},
                status=403,
            )
        _clear_failed_login_attempts(profile)
        django_login(request, user)
        log_audit(
            user,
            "auth.login",
            resource_type="session",
            summary=f"User {user.username} signed in",
            metadata={"username": user.username},
        )
        return Response(
            {
                "success": True,
                "message": "Login successful",
                "user": user_payload(user),
            }
        )

    if existing_user:
        _, is_locked = _record_failed_login_attempt(existing_user)
        if is_locked:
            return Response(
                {"success": False, "message": _lockout_message()},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

    return Response(
        {"success": False, "message": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    log_audit(
        request.user,
        "auth.logout",
        resource_type="session",
        summary=f"User {request.user.username} signed out",
        metadata={"username": request.user.username},
    )
    django_logout(request)
    return Response({"success": True, "message": "Logged out"})


login.csrf_exempt = False
