from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryViewSet, AuthorViewSet, BookViewSet, BorrowingViewSet# BorrowingView

router = DefaultRouter()

router.register('libraries', LibraryViewSet)
router.register('authors', AuthorViewSet)
router.register('books', BookViewSet)
router.register('borrowings', BorrowingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('borrowings/', BorrowingView.as_view(), name='borrowings'),
]
