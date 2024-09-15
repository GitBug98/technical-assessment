from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Library, Author, Book, Borrowing
from .serializers import LibrarySerializer, AuthorSerializer, BookSerializer, BorrowingSerializer
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from .filters import LibraryFilter, BookFilter, AuthorFilter
from django_filters.rest_framework import DjangoFilterBackend
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .pagination import DefaultPagination
from django.db.models import Count, Q
from .tasks import send_borrowing_confirmation_email, send_borrowing_reminder_email
from datetime import timedelta
from rest_framework.exceptions import ValidationError

class LibraryViewSet(viewsets.ModelViewSet):
    queryset = Library.objects.all()  # Default queryset
    serializer_class = LibrarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilter
    search_fields = ['name', 'books__title']
    ordering_fields = ['name', 'books__title']
    http_method_names = ['get', 'post', 'put', 'delete']
    pagination_class = DefaultPagination


    def get_serializer_context(self):
        # Pass the request context to the serializer
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()  # Default queryset
    serializer_class = AuthorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilter
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'last_name']
    http_method_names = ['get', 'post', 'put', 'delete']
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        
        return filtered_queryset.annotate(
            book_count=Count('books')
        ).prefetch_related('books__category', 'books__library')
    
             
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author', 'category', 'library').all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilter
    search_fields = ['title', 'author__first_name', 'author__last_name']
    ordering_fields = ['title', 'available_copies']
    http_method_names = ['get', 'post', 'put', 'delete']
    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
            

        
class BorrowingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling borrowing and returning of books.
    """
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter the borrowing records to only those that belong to the logged-in user.
        """
        return Borrowing.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Ensure the user can borrow a book, and create the borrowing record.
        """
        user = self.request.user
        book = serializer.validated_data['book']

        # Check if there are any available copies of the book
        if book.available_copies < 1:
            raise ValidationError(f"The book '{book.title}' is not available for borrowing.")

        # Decrease available copies when borrowed
        book.available_copies -= 1
        book.save()
        send_borrowing_confirmation_email.delay(user.email, book.title)
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    "type": "notify",
                    "data":  f"Book '{book.title}' has been borrowed successfully."
                }
            )        

        serializer.save(user=user)

    def perform_update(self, serializer):
        """
        Handle the return of the book by marking it as returned and adjusting book availability.
        """
        borrowing = self.get_object()
        if borrowing.returned:
            return Response({"error": "This book has already been returned."}, status=status.HTTP_400_BAD_REQUEST)

        user = self.request.user
        # Check if the book is being returned
        if serializer.validated_data.get('returned', False):
            # Increase the available copies when returned
            borrowing.book.available_copies += 1
            borrowing.book.save()
        elif borrowing.returned:
            raise ValidationError("This book has already been returned.")
        else:
            # Check if the user is trying to update any other field
            if user != borrowing.user:
                raise ValidationError("You are not allowed to update this borrowing record.")
            else:
                raise ValidationError("You can only return a book by updating the 'returned' field.")
        # Update the borrowing record (which may include marking it as returned)
        serializer.save()
