"""Модели каталога: книги и отзывы пользователей."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Book(models.Model):
    """Книга каталога.

    Книги создаются и редактируются только через Django Admin или
    management-команду seed_books — публичный API отдаёт их лишь на
    чтение (books.views.BookListView, BookDetailView).
    """

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title", "id")

    def __str__(self):
        return self.title


class Review(models.Model):
    """Отзыв пользователя на книгу: оценка 1-10 и текст.

    Ограничение «один отзыв на книгу от одного пользователя» и диапазон
    оценки заданы constraints и продублированы на уровне API
    (books.views.BookReviewsView.perform_create,
    books.serializers.ReviewSerializer) — так ошибка валидации становится
    аккуратным 400 с сообщением, а constraint остаётся последней защитой
    от гонки при одновременных запросах.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="one_review_per_user_book"
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=10),
                name="rating_between_1_and_10",
            ),
        ]

    def __str__(self):
        return f"{self.book} — {self.rating}/10"
