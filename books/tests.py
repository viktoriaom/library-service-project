from uuid import uuid4
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from djmoney.money import Money
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOK_URL = reverse("books:book-list")


def detail_url(book_id):
    return reverse("books:book-detail", kwargs={"pk": book_id})


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


class UnauthenticatedBookViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_list_books(self):
        create_test_book()
        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_detail_books(self):
        book = create_test_book()
        res = self.client.get(detail_url(book.id))
        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class AuthenticatedNonAdminBookViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user, self.client = create_and_login_user()

    def test_create_book_non_admin_forbidden(self):
        payload = {
            "title": "Book 1",
            "author": "Author 1",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_book_non_admin_forbidden(self):
        book = create_test_book()
        payload = {
            "title": "Book 1",
            "author": "Author 1",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        res = self.client.put(detail_url(book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_book_non_admin_forbidden(self):
        book = create_test_book()
        payload = {
            "inventory": 100,
        }
        res = self.client.patch(detail_url(book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_non_admin_forbidden(self):
        book = create_test_book()
        res = self.client.delete(detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBookViewSetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user, self.client = create_and_login_user(
            email="admin@example.com", is_staff=True
        )

    def test_create_book_admin(self):
        payload = {
            "title": "Book 1",
            "author": "Author 1",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        res = self.client.post(BOOK_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(title=payload["title"])
        self.assertEqual(book.title, payload["title"])
        self.assertEqual(book.author, payload["author"])
        self.assertEqual(book.cover, payload["cover"])
        self.assertEqual(book.inventory, payload["inventory"])
        self.assertEqual(book.daily_fee, Money(payload["daily_fee"], "USD"))

    def test_create_invalid_book_forbidden(self):
        payload_with_wrong_daily_fee = {
            "title": "Book 1",
            "author": "Author 1",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": -4,
        }
        res = self.client.post(BOOK_URL, payload_with_wrong_daily_fee)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_book_admin(self):
        book = create_test_book()
        payload = {
            "title": "Book 1",
            "author": "Author 1",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": 2.50,
        }
        res = self.client.put(detail_url(book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        book.refresh_from_db()
        self.assertEqual(payload["title"], book.title)
        self.assertEqual(payload["author"], book.author)
        self.assertEqual(payload["cover"], book.cover)
        self.assertEqual(payload["inventory"], book.inventory)
        self.assertEqual(Money(payload["daily_fee"], "USD"), book.daily_fee)

        self.assertEqual(res.data["title"], payload["title"])
        self.assertEqual(res.data["author"], payload["author"])
        self.assertEqual(res.data["cover"], payload["cover"])
        self.assertEqual(res.data["inventory"], payload["inventory"])

    def test_patch_book_admin(self):
        book = create_test_book()
        payload = {
            "inventory": 100,
        }
        res = self.client.patch(detail_url(book.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(payload["inventory"], book.inventory)

    def test_delete_book_admin(self):
        book = create_test_book()
        res = self.client.delete(detail_url(book.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
