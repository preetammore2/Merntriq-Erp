from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.captcha import make_captcha_token
from apps.accounts.models import User, UserRole
from apps.core.models import Campus, CampusMembership


@override_settings(SECRET_KEY="test-secret-key-that-is-at-least-32-bytes")
class LoginCaptchaTests(APITestCase):
    def setUp(self):
        self.school = Campus.objects.create(name="Login Test School", code="LOGIN")
        self.user = User.objects.create_user(
            username="login.admin",
            password="Passw0rd!123",
            role=UserRole.SCHOOL_ADMIN,
            school=self.school,
            is_staff=True,
        )
        CampusMembership.objects.create(
            campus=self.school,
            user=self.user,
            role="it_admin",
            is_primary=True,
            can_manage_users=True,
            can_configure_attendance=True,
        )

    def test_captcha_challenge_is_public_and_contains_numeric_code(self):
        response = self.client.get("/api/v1/auth/captcha/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("challenge_id", response.data)
        self.assertIn("expires_in", response.data)
        self.assertIn("code", response.data)
        self.assertRegex(response.data["code"], r"^\d{5}$")

    def test_login_requires_valid_captcha(self):
        missing = self.client.post(
            "/api/v1/auth/token/",
            {"username": "login.admin", "password": "Passw0rd!123"},
            format="json",
        )
        invalid = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "login.admin",
                "password": "Passw0rd!123",
                "captcha_id": make_captcha_token("73941"),
                "captcha_answer": "WRONG",
            },
            format="json",
        )

        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_accepts_valid_captcha(self):
        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "login.admin",
                "password": "Passw0rd!123",
                "captcha_id": make_captcha_token("73941"),
                "captcha_answer": "73941",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["username"], "login.admin")

    def test_login_rejects_inactive_school(self):
        self.school.status = "inactive"
        self.school.save(update_fields=["status", "updated_at"])

        response = self.client.post(
            "/api/v1/auth/token/",
            {
                "username": "login.admin",
                "password": "Passw0rd!123",
                "captcha_id": make_captcha_token("73941"),
                "captcha_answer": "73941",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SuperAdminProtectionTests(APITestCase):
    def setUp(self):
        self.super_admin = User.objects.create_user(
            username="protected.super",
            password="Passw0rd!123",
            role=UserRole.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=self.super_admin)

    def test_super_admin_cannot_be_disabled_or_deleted(self):
        disable_response = self.client.patch(
            f"/api/v1/auth/users/{self.super_admin.id}/",
            {"is_active": False},
            format="json",
        )
        delete_response = self.client.delete(f"/api/v1/auth/users/{self.super_admin.id}/")

        self.assertEqual(disable_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)

        self.super_admin.refresh_from_db()
        self.assertTrue(self.super_admin.is_active)
        self.assertEqual(self.super_admin.role, UserRole.SUPER_ADMIN)

    def test_super_admin_cannot_be_modified_by_another_user(self):
        other_super_admin = User.objects.create_user(
            username="other.super",
            password="Passw0rd!123",
            role=UserRole.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_authenticate(user=other_super_admin)

        response = self.client.patch(
            f"/api/v1/auth/users/{self.super_admin.id}/",
            {"first_name": "Tampered"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.super_admin.refresh_from_db()
        self.assertEqual(self.super_admin.first_name, "")
