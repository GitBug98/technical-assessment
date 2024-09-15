from rest_framework import serializers
from .models import Library, Author, Book, Category, Borrowing
from django.utils import timezone
from datetime import timedelta
from geopy.distance import geodesic


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        ref_name = 'Category'

class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'available_copies']
        ref_name = 'Book'


class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True)
    book_count = serializers.IntegerField()
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'books', 'book_count']
        ref_name = 'Author'
        read_only_fields = ['book_count']

class AuthorBookSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name']
        ref_name = 'Author'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorBookSerializer()
    category = CategorySerializer()

    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'category', 'available_copies']
        ref_name = 'Book'

class LibrarySerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    class Meta:
        model = Library
        fields = ['id', 'name', 'address', 'city', 'state', 'zip_code', 'location','distance']
        ref_name = 'Library'
    
    def get_distance(self, obj):
        user = self.context['request'].user
        if user.location and obj.location:
            user_location = tuple(map(float, user.location.split(',')))  # Convert "lat,long" to (lat, long) tuple
            library_location = tuple(map(float, obj.location.split(',')))  # Same for the library location
            distance = geodesic(user_location, library_location).km  # Distance in kilometers
            distance = round(distance, 2)
            return distance        
        return None



# class BorrowingSerializer(serializers.ModelSerializer):
#     book = BookSerializer(read_only=True)
#     penalty = serializers.SerializerMethodField()

#     class Meta:
#         model = Borrowing
#         fields = ['id', 'user', 'book', 'borrowed_at', 'return_due', 'returned', 'penalty']
#         read_only_fields = ['penalty', 'returned', 'borrowed_at', 'return_due', 'user']

#     def get_penalty(self, obj):
#         return obj.calculate_penalty()

#     def create(self, validated_data):
#         borrowing = Borrowing.objects.create(**validated_data)
#         borrowing.return_due = timezone.now() + timedelta(days=14)
#         borrowing.save()
#         return borrowing
    
    
class BorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')
    penalty = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    returned = serializers.BooleanField(default=False)
    
    class Meta:
        model = Borrowing
        fields = ['id', 'book', 'book_title', 'borrowed_at', 'return_due', 'returned', 'penalty']
        read_only_fields = ['borrowed_at', 'penalty']
    
    def validate(self, data):
        """
        Add custom validation to ensure the user is allowed to borrow a book.
        """
        user = self.context['request'].user
        # Ensure the user is not borrowing more than 3 books at a time.
        if not self.instance and user.borrowings.filter(returned=False).count() >= 3:
            raise serializers.ValidationError("You cannot borrow more than 3 books at a time.")

        # Ensure the return_due date is within 1 month
        if 'return_due' in data:
            if data['return_due'] > (timezone.now() + timedelta(days=30)):
                raise serializers.ValidationError("You cannot borrow a book for more than 1 month.")
        request = self.context.get('request')            
        
        # Check if the current user is the owner of the borrowing record
        if self.instance and self.instance.user != request.user:
            raise serializers.ValidationError("You cannot return a book borrowed by another user.")
        
        # Check if the book is already returned
        if self.instance and self.instance.returned and data.get('returned') == True:
            raise serializers.ValidationError("This book has already been returned.")
        
        return data

    def update(self, instance, validated_data):
        """
        Handle the return of a book, and recalculate penalties.
        """
        instance.returned = validated_data.get('returned', instance.returned)
        
        # Calculate penalty if the book is being returned late
        if instance.returned:
            instance.penalty = instance.calculate_penalty()

        instance.save()
        return instance