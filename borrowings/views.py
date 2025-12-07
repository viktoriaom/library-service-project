from django.db import transaction
from rest_framework import viewsets, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer
)


class BorrowingsReadSet(viewsets.ReadOnlyModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Borrowing.objects.all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        else:
            user_id_str = self.request.query_params.get("user_id")
            if user_id_str:
                try:
                    queryset = queryset.filter(user__id=int(user_id_str))
                except ValueError:
                    queryset = queryset.none()

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset.select_related("book", "user")


class BorrowingsCreateView(generics.CreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingCreateSerializer
    permission_classes = [IsAuthenticated]

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
