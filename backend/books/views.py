"""Вьюхи каталога книг и отзывов."""

from django.db import IntegrityError, transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers

from .models import Book, Review
from .permissions import IsReviewOwner
from .serializers import BookSerializer, ReviewSerializer


class BookListView(generics.ListAPIView):
    """`GET /api/books/` — публичный список книг с рейтингом и числом отзывов.

    Каталог доступен только на чтение: изменить книги через этот или
    любой другой API-эндпоинт нельзя (405), только через Django Admin
    или management-команду seed_books.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer
    queryset = Book.objects.annotate(
        average_rating=Avg("reviews__rating"),
        reviews_count=Count("reviews"),
    ).order_by("title", "id")


class BookDetailView(generics.RetrieveAPIView):
    """`GET /api/books/{id}/` — одна книга с теми же агрегатами, что и в списке."""

    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer
    queryset = BookListView.queryset


class BookReviewsView(generics.ListCreateAPIView):
    """`GET/POST /api/books/{book_id}/reviews/` — отзывы конкретной книги.

    GET публичен, POST требует входа (IsAuthenticatedOrReadOnly).
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Отзывы книги из URL; 404, если такой книги нет."""
        book = get_object_or_404(Book, pk=self.kwargs["book_id"])
        return book.reviews.select_related("user")

    def perform_create(self, serializer):
        """Создаёт отзыв от имени текущего пользователя на книгу из URL.

        Автор и книга берутся не из тела запроса, а из request.user и
        URL — так подделать их через API нельзя (см. тест
        test_create_review_ignores_forged_author_and_book).

        Raises:
            serializers.ValidationError: 400, если пользователь уже
                оставлял отзыв на эту книгу. Проверяется дважды: сразу
                через exists(), а затем через перехват IntegrityError —
                на случай, если два запроса от одного пользователя
                придут одновременно и оба пройдут первую проверку.
        """
        book = get_object_or_404(Book, pk=self.kwargs["book_id"])
        if Review.objects.filter(user=self.request.user, book=book).exists():
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this book."}
            )
        try:
            with transaction.atomic():
                serializer.save(user=self.request.user, book=book)
        except IntegrityError:
            # UniqueConstraint remains the final guard for concurrent requests.
            raise serializers.ValidationError(
                {"detail": "You have already reviewed this book."}
            )


class ReviewDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    """`PATCH/DELETE /api/reviews/{id}/` — изменение и удаление своего отзыва.

    IsReviewOwner (books.permissions) отклоняет запрос с 403, если
    пользователь не автор отзыва — даже для staff-пользователей
    исключений нет. GET/PUT не поддерживаются: http_method_names
    ограничивает набор методов явно.
    """

    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("user")
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    http_method_names = ["patch", "delete", "options"]
