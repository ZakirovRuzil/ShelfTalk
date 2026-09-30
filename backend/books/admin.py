"""Регистрация Book и Review в Django Admin — способ управлять каталогом."""

from django.contrib import admin

from .models import Book, Review


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Список книг в админке с поиском по названию и автору."""

    list_display = ("title", "author", "publication_year")
    search_fields = ("title", "author")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Список отзывов в админке (для модерации)."""

    list_display = ("book", "user", "rating", "created_at")
    list_select_related = ("book", "user")
