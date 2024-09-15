from django.db import models
from users.models import User
from django.utils import timezone
from location_field.models.plain import PlainLocationField

class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    location = PlainLocationField(based_fields=['city'], zoom=7, null=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    library = models.ForeignKey('Library', on_delete=models.CASCADE, related_name='books')
    available_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrowings')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    return_due = models.DateTimeField()
    returned = models.BooleanField(default=False)
    penalty = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.full_name} borrowed {self.book.title}"

    def calculate_penalty(self):
        if self.returned:
            return 0
        overdue_days = (timezone.now().date() - self.return_due.date()).days
        return max(0, overdue_days * 1) 