from django.core.validators import MinValueValidator
from django.db import models
from djmoney.models.fields import MoneyField


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=4,
                             choices=Cover.choices,
                             default=Cover.HARD
                             )
    inventory = models.PositiveIntegerField()
    daily_fee = MoneyField(
        max_digits=10,
        decimal_places=2,
        default_currency="USD",
        validators=[MinValueValidator(0)]
    )
