# portal/app/urls.py
from django.urls import path

from .google_auth import login_with_google
from .login_auth import login, logout
from .me_view import me_view
from .registration_views import (
    csrf_token_view,
    password_reset_confirm,
    password_reset_request,
    register,
    resend_verification,
    verify_email,
)
from .platform_views import (
    AuditLogListView,
    MarkAllNotificationsReadView,
    NotificationDetailView,
    NotificationListView,
    PlatformSettingsDetailView,
    UserPreferencesDetailView,
)
from .user_views import UserListCreateView, UserRetrieveUpdateDestroyView

urlpatterns = [
    path("csrf/", csrf_token_view, name="csrf"),
    path("login/", login, name="login"),
    path("auth/google/", login_with_google, name="auth-google"),
    path("logout/", logout, name="logout"),
    path("register/", register, name="register"),
    path("verify-email/", verify_email, name="verify-email"),
    path(
        "resend-verification/",
        resend_verification,
        name="resend-verification",
    ),
    path("password-reset/", password_reset_request, name="password-reset"),
    path(
        "password-reset/confirm/",
        password_reset_confirm,
        name="password-reset-confirm",
    ),
    path("me/", me_view, name="me"),
    path("users/", UserListCreateView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserRetrieveUpdateDestroyView.as_view(), name="users-detail"),
    path(
        "notifications/mark-all-read/",
        MarkAllNotificationsReadView.as_view(),
        name="notifications-mark-all-read",
    ),
    path(
        "notifications/<int:pk>/",
        NotificationDetailView.as_view(),
        name="notifications-detail",
    ),
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path(
        "preferences/me/",
        UserPreferencesDetailView.as_view(),
        name="preferences-me",
    ),
    path(
        "platform-settings/",
        PlatformSettingsDetailView.as_view(),
        name="platform-settings",
    ),
    path("audit-logs/", AuditLogListView.as_view(), name="audit-logs-list"),
]
