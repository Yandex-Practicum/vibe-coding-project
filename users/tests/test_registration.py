import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("users:register")

    def test_successful_registration(self):
        response = self.client.post(
            self.url,
            data=json.dumps(
                {"email": "  Student@Example.COM ", "password": "safe-pass-123"}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "student@example.com")
        user = User.objects.get()
        self.assertEqual(user.username, "student@example.com")
        self.assertTrue(user.check_password("safe-pass-123"))

    def test_invalid_json_returns_400(self):
        response = self.client.post(
            self.url,
            data="{not-json}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "invalid_json"})

    def test_short_password_returns_400(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"email": "student@example.com", "password": "short"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "password_too_short"})
        self.assertFalse(User.objects.exists())
