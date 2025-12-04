from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import BorrowingsReadSet

router = DefaultRouter()
router.register("borrowings", BorrowingsReadSet)
urlpatterns = [path("", include(router.urls))]

app_name = "borrowings"
