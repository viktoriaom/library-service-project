from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.utils.translation import gettext_lazy as _
from books.models import Book
from user.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(expected_return_date__gt=F("borrow_date")),
                name="expected_return_after_borrow",
            ),
            CheckConstraint(
                check=Q(actual_return_date__isnull=True)
                | Q(actual_return_date__gt=F("borrow_date")),
                name="actual_return_after_borrow",
            ),
        ]

    def clean(self):
        super().clean()

        if self.expected_return_date and self.borrow_date:
            if self.expected_return_date <= self.borrow_date:
                raise ValidationError(
                    {
                        "expected_return_date": _(
                            "Expected return date must be after borrow date."
                        )
                    }
                )

        if self.actual_return_date:
            if self.actual_return_date < self.borrow_date:
                raise ValidationError(
                    {
                        "actual_return_date": _(
                            "Actual return date cannot be before borrow date."
                        )
                    }
                )

    def __str__(self):
        return f"{self.user} borrowed {self.book} on {self.borrow_date}"
