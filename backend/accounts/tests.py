from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def setUp(self):
        self.data = {
            "email": "reader@example.com",
            "display_name": "Reader",
            "password": "A-good-book-2026!",
        }

    def register(self):
        return self.client.post("/api/auth/register/", self.data)

    def test_registration_hashes_password_and_exposes_only_safe_fields(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("password", response.data)
        user = User.objects.get()
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotEqual(user.password, self.data["password"])
        self.assertNotIn("username", [field.name for field in User._meta.fields])
        self.assertFalse(user.is_staff)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        self.register()
        for email in (self.data["email"], "READER@EXAMPLE.COM"):
            response = self.client.post(
                "/api/auth/register/", {**self.data, "email": email}
            )
            self.assertEqual(response.status_code, 400)
            self.assertIn("email", response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_email_uniqueness_is_enforced_by_database(self):
        self.register()
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.bulk_create(
                [User(email="READER@EXAMPLE.COM", display_name="Other")]
            )

    def test_invalid_registration_and_privilege_injection(self):
        for changes in (
            {"email": "invalid"},
            {"display_name": " "},
            {"password": "123"},
        ):
            self.assertEqual(
                self.client.post(
                    "/api/auth/register/", {**self.data, **changes}
                ).status_code,
                400,
            )
        response = self.client.post(
            "/api/auth/register/", {**self.data, "is_staff": True, "is_superuser": True}
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(User.objects.get().is_superuser)

    def test_login_me_and_refresh_use_real_jwt(self):
        self.register()
        response = self.client.post(
            "/api/auth/login/", {**self.data, "email": "READER@EXAMPLE.COM"}
        )
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        me = self.client.get("/api/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["email"], self.data["email"])
        self.assertNotIn("password", me.data)
        refreshed = self.client.post(
            "/api/auth/refresh/", {"refresh": response.data["refresh"]}
        )
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn("access", refreshed.data)

    def test_wrong_password_and_anonymous_me_are_rejected(self):
        self.register()
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/api/auth/login/", {**self.data, "password": "wrong"}
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.post("/api/auth/refresh/", {"refresh": "invalid"}).status_code,
            401,
        )

    def test_user_manager_and_superuser(self):
        user = User.objects.create_superuser("ADMIN@EXAMPLE.COM", "A-good-book-2026!")
        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff and user.is_superuser)
        with self.assertRaises(ValueError):
            User.objects.create_user("")
        with self.assertRaises(ValueError):
            User.objects.create_superuser("bad@example.com", is_staff=False)

    def test_custom_user_admin_forms(self):
        from .admin import CustomUserChangeForm, CustomUserCreationForm

        form = CustomUserCreationForm(
            data={
                **self.data,
                "password1": self.data["password"],
                "password2": self.data["password"],
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotIn("username", CustomUserChangeForm(instance=user).fields)
