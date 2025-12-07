from django.utils import timezone

from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer, BorrowingReturnSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="user_id",
                type={"type": "int"},
                description="Filter for admins by user_id (ex. ?user_id=1)",
            ),
            OpenApiParameter(
                name="is_active",
                type={"type": "str"},
                description="Filter only active borrowings (ex. ?is_active=true)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances."""
        return super().list(request, *args, **kwargs)


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


class BorrowingsReturnView(generics.RetrieveUpdateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingReturnSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Borrowing.objects.filter(actual_return_date__isnull=True)
        return Borrowing.objects.filter(
            user=self.request.user,
            actual_return_date__isnull=True
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.actual_return_date is not None:
            raise ValidationError({
                "detail": "This borrowing has already been returned."
            })

        with transaction.atomic():
            book = instance.book
            book.inventory += 1
            book.save()

            instance.actual_return_date = timezone.now().date()
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(
            {"message": "Book returned successfully",
             "borrowing": serializer.data
             },
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
