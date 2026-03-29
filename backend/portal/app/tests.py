from datetime import timedelta
import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from .models import AuditLog, PlatformSettings, Profile


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.csrf_client = Client(enforce_csrf_checks=True)

    def _csrf_token(self):
        response = self.csrf_client.get("/api/csrf/")
        self.assertEqual(response.status_code, 200)
        return response.cookies["csrftoken"].value

    def test_register_verify_login_and_bootstrap_me(self):
        csrf_token = self._csrf_token()

        with patch("app.registration_views.generate_code", return_value="123456"):
            response = self.csrf_client.post(
                "/api/register/",
                data=json.dumps(
                    {
                        "username": "newuser",
                        "email": "newuser@example.com",
                        "password": "strong-pass-123",
                        "password_confirm": "strong-pass-123",
                    }
                ),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf_token,
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("123456", mail.outbox[0].body)

        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)
        self.assertFalse(user.profile.email_verified)

        verify_response = self.csrf_client.post(
            "/api/verify-email/",
            data=json.dumps({"email": "newuser@example.com", "code": "123456"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(verify_response.status_code, 200)

        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.email_verified)

        login_response = self.csrf_client.post(
            "/api/login/",
            data=json.dumps({"username": "newuser", "password": "strong-pass-123"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()["user"]["username"], "newuser")

        me_response = self.csrf_client.get("/api/me/")
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.json()["email"], "newuser@example.com")

        actions = list(
            AuditLog.objects.order_by("created_at").values_list("action", flat=True)
        )
        self.assertIn("auth.register", actions)
        self.assertIn("auth.email_verified", actions)
        self.assertIn("auth.login", actions)

    def test_register_requires_csrf(self):
        response = self.csrf_client.post(
            "/api/register/",
            data=json.dumps(
                {
                    "username": "csrfuser",
                    "email": "csrfuser@example.com",
                    "password": "strong-pass-123",
                    "password_confirm": "strong-pass-123",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_registration_can_be_disabled_via_platform_settings(self):
        settings_obj = PlatformSettings.get_solo()
        settings_obj.feature_flags["registration_enabled"] = False
        settings_obj.save()

        csrf_token = self._csrf_token()
        response = self.csrf_client.post(
            "/api/register/",
            data=json.dumps(
                {
                    "username": "blocked-user",
                    "email": "blocked@example.com",
                    "password": "strong-pass-123",
                    "password_confirm": "strong-pass-123",
                }
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("disabled", response.json()["message"].lower())

    @override_settings(LOGIN_MAX_FAILED_ATTEMPTS=3, LOGIN_LOCKOUT_MINUTES=15)
    def test_login_locks_after_repeated_failures_and_sends_reset_email(self):
        settings_obj = PlatformSettings.get_solo()
        settings_obj.login_max_failed_attempts = 3
        settings_obj.login_lockout_minutes = 15
        settings_obj.save()

        user = User.objects.create_user(
            username="locked-user",
            email="locked@example.com",
            password="strong-pass-123",
            is_active=True,
        )
        user.profile.email_verified = True
        user.profile.save(update_fields=["email_verified"])

        csrf_token = self._csrf_token()
        for _ in range(2):
            response = self.csrf_client.post(
                "/api/login/",
                data=json.dumps({"username": "locked-user", "password": "wrong-pass"}),
                content_type="application/json",
                HTTP_X_CSRFTOKEN=csrf_token,
            )
            self.assertEqual(response.status_code, 401)

        locked = self.csrf_client.post(
            "/api/login/",
            data=json.dumps({"username": "locked-user", "password": "wrong-pass"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(locked.status_code, 429)
        self.assertIn("recovery instructions", locked.json()["message"])

        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.failed_login_attempts, 3)
        self.assertIsNotNone(user.profile.login_locked_until)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset your password", mail.outbox[0].body.lower())

        blocked = self.csrf_client.post(
            "/api/login/",
            data=json.dumps({"username": "locked-user", "password": "strong-pass-123"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(blocked.status_code, 429)

    @override_settings(LOGIN_MAX_FAILED_ATTEMPTS=2, LOGIN_LOCKOUT_MINUTES=15)
    def test_unverified_user_lockout_resends_verification_email(self):
        settings_obj = PlatformSettings.get_solo()
        settings_obj.login_max_failed_attempts = 2
        settings_obj.login_lockout_minutes = 15
        settings_obj.save()

        user = User.objects.create_user(
            username="pending-user",
            email="pending@example.com",
            password="strong-pass-123",
            is_active=False,
        )
        user.profile.email_verified = False
        user.profile.save(update_fields=["email_verified"])

        csrf_token = self._csrf_token()
        with patch("app.login_auth.generate_code", return_value="654321"):
            for _ in range(2):
                response = self.csrf_client.post(
                    "/api/login/",
                    data=json.dumps({"username": "pending-user", "password": "wrong-pass"}),
                    content_type="application/json",
                    HTTP_X_CSRFTOKEN=csrf_token,
                )

        self.assertEqual(response.status_code, 429)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("654321", mail.outbox[0].body)

        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertTrue(user.profile.email_verification_code_hash)
        self.assertIsNotNone(user.profile.login_locked_until)

    @override_settings(LOGIN_MAX_FAILED_ATTEMPTS=2, LOGIN_LOCKOUT_MINUTES=15)
    def test_lockout_expires_and_successful_login_clears_counter(self):
        settings_obj = PlatformSettings.get_solo()
        settings_obj.login_max_failed_attempts = 2
        settings_obj.login_lockout_minutes = 15
        settings_obj.save()

        user = User.objects.create_user(
            username="cooldown-user",
            email="cooldown@example.com",
            password="strong-pass-123",
            is_active=True,
        )
        user.profile.email_verified = True
        user.profile.failed_login_attempts = 2
        user.profile.login_locked_until = timezone.now() - timedelta(minutes=1)
        user.profile.save(
            update_fields=["email_verified", "failed_login_attempts", "login_locked_until"]
        )

        csrf_token = self._csrf_token()
        response = self.csrf_client.post(
            "/api/login/",
            data=json.dumps({"username": "cooldown-user", "password": "strong-pass-123"}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.failed_login_attempts, 0)
        self.assertIsNone(user.profile.login_locked_until)

    def test_me_patch_updates_user_and_profile_fields(self):
        user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="strong-pass-123",
            is_active=True,
        )
        user.profile.email_verified = True
        user.profile.save(update_fields=["email_verified"])

        self.client.force_authenticate(user=user)
        response = self.client.patch(
            "/api/me/",
            {
                "first_name": "Alice",
                "last_name": "Ngugi",
                "phone": "+254700000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        user.profile.refresh_from_db()
        self.assertEqual(user.first_name, "Alice")
        self.assertEqual(user.last_name, "Ngugi")
        self.assertEqual(user.profile.phone, "+254700000000")
        self.assertTrue(
            AuditLog.objects.filter(
                actor=user,
                action="profile.update",
            ).exists()
        )


class UserManagementPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def _create_user(self, username: str, role: str) -> User:
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="strong-pass-123",
            is_active=True,
        )
        profile = user.profile
        profile.role = role
        profile.email_verified = True
        profile.save(update_fields=["role", "email_verified"])
        return user

    def test_admin_cannot_create_admin_accounts(self):
        admin_user = self._create_user("manager", Profile.ROLE_ADMIN)
        self.client.force_authenticate(user=admin_user)

        response = self.client.post(
            "/api/users/",
            {
                "username": "bad-admin",
                "password": "strong-pass-123",
                "email": "bad-admin@example.com",
                "role": "admin",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data)

    def test_admin_cannot_manage_other_admin_accounts(self):
        acting_admin = self._create_user("manager", Profile.ROLE_ADMIN)
        target_admin = self._create_user("second-admin", Profile.ROLE_ADMIN)
        self.client.force_authenticate(user=acting_admin)

        response = self.client.patch(
            f"/api/users/{target_admin.pk}/",
            {"first_name": "Blocked"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

    def test_admin_can_create_customer_account(self):
        admin_user = self._create_user("manager", Profile.ROLE_ADMIN)
        self.client.force_authenticate(user=admin_user)

        response = self.client.post(
            "/api/users/",
            {
                "username": "customer1",
                "password": "strong-pass-123",
                "email": "customer1@example.com",
                "role": "customer",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        created = User.objects.get(username="customer1")
        self.assertEqual(created.profile.role, Profile.ROLE_CUSTOMER)
        self.assertTrue(created.profile.email_verified)

    def test_only_superadmin_can_update_platform_lockout_settings(self):
        superadmin = self._create_user("root-admin", Profile.ROLE_SUPERADMIN)
        admin_user = self._create_user("manager", Profile.ROLE_ADMIN)

        self.client.force_authenticate(user=admin_user)
        forbidden = self.client.patch(
            "/api/platform-settings/",
            {"login_max_failed_attempts": 7},
            format="json",
        )
        self.assertEqual(forbidden.status_code, 403)

        self.client.force_authenticate(user=superadmin)
        allowed = self.client.patch(
            "/api/platform-settings/",
            {
                "login_max_failed_attempts": 7,
                "login_lockout_minutes": 20,
            },
            format="json",
        )
        self.assertEqual(allowed.status_code, 200)

        settings_obj = PlatformSettings.get_solo()
        self.assertEqual(settings_obj.login_max_failed_attempts, 7)
        self.assertEqual(settings_obj.login_lockout_minutes, 20)

    def test_dynamic_role_permissions_can_disable_admin_user_management(self):
        admin_user = self._create_user("manager", Profile.ROLE_ADMIN)
        settings_obj = PlatformSettings.get_solo()
        settings_obj.role_permissions[Profile.ROLE_ADMIN] = ["audit.view"]
        settings_obj.save()

        self.client.force_authenticate(user=admin_user)
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 403)

    def test_dynamic_role_permissions_can_enable_staff_audit_access(self):
        staff_user = self._create_user("auditor", Profile.ROLE_STAFF)
        settings_obj = PlatformSettings.get_solo()
        settings_obj.role_permissions[Profile.ROLE_STAFF] = ["audit.view"]
        settings_obj.save()

        self.client.force_authenticate(user=staff_user)
        response = self.client.get("/api/audit-logs/")
        self.assertEqual(response.status_code, 200)
