"""Сериализаторы каталога книг и отзывов."""

from rest_framework import serializers

from accounts.models import User

from .models import Book, Review


class BookSerializer(serializers.ModelSerializer):
    """Книга вместе с агрегатами по отзывам.

    average_rating и reviews_count — не поля модели, а аннотации,
    добавленные к queryset в books.views.BookListView (Avg/Count по
    reviews). average_rating равен null, пока у книги нет ни одного
    отзыва.
    """

    average_rating = serializers.FloatField(read_only=True, allow_null=True)
    reviews_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "description",
            "publication_year",
            "average_rating",
            "reviews_count",
        )


class ReviewAuthorSerializer(serializers.ModelSerializer):
    """Автор отзыва в публичном виде: без email и других приватных полей."""

    class Meta:
        model = User
        fields = ("id", "display_name")


class ReviewSerializer(serializers.ModelSerializer):
    """Отзыв на книгу.

    Поле author только для чтения и берётся из request.user
    (books.views.BookReviewsView.perform_create), а не из тела запроса —
    подделать автора через API нельзя.
    """

    author = ReviewAuthorSerializer(source="user", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "rating", "text", "author", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
