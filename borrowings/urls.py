from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import BorrowingsReadSet, BorrowingsCreateView

router = DefaultRouter()
router.register("borrowings", BorrowingsReadSet)
urlpatterns = [path("", include(router.urls)),
               path("create/", BorrowingsCreateView.as_view(), name="borrowings-create"),
               ]

app_name = "borrowings"
