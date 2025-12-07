from django.utils import timezone
from rest_framework import serializers

from books.serializers import BookSerializer
from borrowings.models import Borrowing
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "book",
        ]


class BorrowingReturnSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    fee_to_pay = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "fee_to_pay",
        ]
        read_only_fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "fee_to_pay",
        ]

    def get_fee_to_pay(self, obj):
        return_date = obj.actual_return_date if (
            obj.actual_return_date) else (
            timezone.now().date())
        days_borrowed = (return_date - obj.borrow_date).days
        total_fee = days_borrowed * float(obj.book.daily_fee.amount)
        return round(total_fee, 2)
