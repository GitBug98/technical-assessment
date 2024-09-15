from django.contrib import admin
from .models import Author, Book, Borrowing, Category, Library
# Register your models here.

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Borrowing)
admin.site.register(Category)
admin.site.register(Library)
