from uuid import uuid4
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

BORROWINGS_URL = reverse("borrowings:borrowing-list")

def create_and_login_user(**params):
    defaults = {
        "email": f"user_{uuid4().hex[:8]}@example.com",
        "password": "testpass123",
        "is_staff": False,
    }
    defaults.update(params)
    client = APIClient()
    user = get_user_model().objects.create_user(**defaults)
    response = client.post(
        "/api/user/token/",
        {"email": defaults["email"], "password": defaults["password"]},
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZE=f"Bearer {token}")
    return user, client


class GetTokensTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_tokens(self):
        get_user_model().objects.create_user(
            email="test@example.com", password="testpass123"
        )
        response = self.client.post(
            "/api/user/token/",
            {"email": "test@example.com", "password": "testpass123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_token = response.data["refresh"]

        refresh_res = self.client.post(
            "/api/user/token/refresh/", {"refresh": refresh_token}
        )

        self.assertEqual(refresh_res.status_code, 200)
        self.assertIn("access", refresh_res.data)

    def test_list_borrowings_missing_token(self):
        self.client.credentials()  # Remove token
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZE="Bearer invalidtoken123")
        res = self.client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_borrowings_correct_token(self):
        user, client = create_and_login_user()
        res = client.get(BORROWINGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
