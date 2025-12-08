from datetime import timedelta

from django.test import TestCase
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", kwargs={"pk": borrowing_id})

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

def create_test_book(**params) -> Book:
    defaults = {"title": f"Book {uuid4().hex[:6]}",
                "author": f"Author {uuid4().hex[:6]}",
                "cover": "HARD",
                "inventory": 10,
                "daily_fee": 2.50,
                }
    defaults.update(params)
    return Book.objects.create(**defaults)


def create_test_borrowing(**params) -> Borrowing:
    if "user" not in params:
        user, client = create_and_login_user()
        params["user"] = user

    if "book" not in params:
        book = create_test_book()
        params["book"] = book

    defaults = {"expected_return_date": (timezone.now().date() + timedelta(days=10))}
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_list_borrowings_forbidden(self):
        create_test_borrowing()
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedNonAdminBorrowingViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user, self.client = create_and_login_user()

    def test_list_borrowings(self):
        create_test_borrowing(user=self.user)
        res = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_borrowings(self):
        borrowing = create_test_borrowing(user=self.user)
        res = self.client.get(detail_url(borrowing.id))
        serializer = BorrowingSerializer(borrowing)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self):
        book = create_test_book()
        payload = {
            "book": book.id,
            "expected_return_date": (timezone.now().date() + timedelta(days=10))
        }
        borrowing_create_url = reverse("borrowings:borrowings-create")
        res = self.client.post(borrowing_create_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # def test_return_borrowing(self):
    #     borrowing = create_test_borrowing(user=self.user)
    #     borrowing_return_url = reverse("borrowings:borrowings-return", kwargs={"pk": borrowing.id})
    #     res = self.client.put(borrowing_return_url)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)


class AdminBorrowingViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user, self.client = create_and_login_user(
            email="admin@example.com", is_staff=True
        )

    def test_list_all_borrowings_admin(self):
        first_user, _ = create_and_login_user()
        second_user, _ = create_and_login_user()

        create_test_borrowing(user=first_user)
        create_test_borrowing(user=second_user)

        borrowing = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowing, many=True)

        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

