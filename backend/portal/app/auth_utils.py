from .models import PlatformSettings, Profile


def get_platform_settings():
    return PlatformSettings.get_solo()


def get_profile_role(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"role": Profile.ROLE_CUSTOMER},
    )
    return profile.role


def is_superadmin(user):
    return get_profile_role(user) == Profile.ROLE_SUPERADMIN


def is_admin(user):
    return get_profile_role(user) == Profile.ROLE_ADMIN


def get_role_permissions(role: str) -> set[str]:
    settings_obj = get_platform_settings()
    configured = settings_obj.role_permissions or {}
    if role in configured:
        return set(configured.get(role, []))
    return set(PlatformSettings.DEFAULT_ROLE_PERMISSIONS.get(role, []))


def has_permission(user, permission: str) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = get_profile_role(user)
    return permission in get_role_permissions(role)


def can_manage_users(user):
    return has_permission(user, "users.manage_all") or has_permission(
        user, "users.manage_limited"
    )


def can_manage_all_users(user):
    return has_permission(user, "users.manage_all")


def can_view_audit_log(user):
    return has_permission(user, "audit.view")


def can_manage_platform(user):
    return has_permission(user, "platform.manage")


def feature_enabled(flag: str) -> bool:
    settings_obj = get_platform_settings()
    configured = settings_obj.feature_flags or {}
    if flag in configured:
        return bool(configured.get(flag))
    return bool(PlatformSettings.DEFAULT_FEATURE_FLAGS.get(flag, False))


def user_payload(user):
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={"role": Profile.ROLE_CUSTOMER},
    )
    settings_obj = get_platform_settings()
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email or "",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "role": profile.role,
        "phone": profile.phone or "",
        "email_verified": profile.email_verified,
        "google_linked": bool(profile.google_sub),
        "permissions": sorted(get_role_permissions(profile.role)),
        "feature_flags": settings_obj.feature_flags,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }
