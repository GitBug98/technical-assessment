import django_filters
from .models import Library, Book, Author, Category

class LibraryFilter(django_filters.FilterSet):
    book_category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.distinct(),  # Ensure categories are distinct
        field_name='books__category'
    )
    book_author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.distinct(),  # Ensure authors are distinct
        field_name='books__author'
    )

    class Meta:
        model = Library
        fields = ['book_category', 'book_author']

class BookFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='category'
    )
    library = django_filters.ModelChoiceFilter(
        queryset=Library.objects.all(),
        field_name='library'
    )
    author = django_filters.ModelChoiceFilter(
        queryset=Author.objects.all(),
        field_name='author'
    )

    class Meta:
        model = Book
        fields = ['category', 'library', 'author']
        

class AuthorFilter(django_filters.FilterSet):
    library = django_filters.ModelChoiceFilter(
        queryset=Library.objects.all(),
        field_name='books__library'
    )
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name='books__category'
    )

    class Meta:
        model = Author
        fields = ['library', 'category']