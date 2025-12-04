from django.db import transaction
from rest_framework import viewsets, generics
from rest_framework.exceptions import ValidationError

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer
)


class BorrowingsReadSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer


class BorrowingsCreateView(generics.CreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            book = serializer.validated_data['book']
            book = Book.objects.select_for_update().get(id=book.id)
            if book.inventory > 0:
                book.inventory -= 1
                book.save()
                serializer.save(user=self.request.user)
            else:
                raise ValidationError(
                    {"book": "Unfortunately, no copies left to borrow."}
                )
