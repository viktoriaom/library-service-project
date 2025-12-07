from django.urls import path, include
from rest_framework.routers import DefaultRouter

from borrowings.views import (
    BorrowingsReadSet,
    BorrowingsCreateView,
    BorrowingsReturnView
)

router = DefaultRouter()
router.register("borrowings", BorrowingsReadSet)
urlpatterns = [path("", include(router.urls)),
               path("create/",
                    BorrowingsCreateView.as_view(),
                    name="borrowings-create"),
               path("<int:pk>/return/",
                    BorrowingsReturnView.as_view(),
                    name="borrowings-return"
                    )
               ]

app_name = "borrowings"
