from django.db import IntegrityError, transaction
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, serializers

from .models import Book, Review
from .permissions import IsReviewOwner
from .serializers import BookSerializer, ReviewSerializer


class BookListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer
    queryset = Book.objects.annotate(
        average_rating=Avg("reviews__rating"),
        reviews_count=Count("reviews"),
    ).order_by("title", "id")


class BookDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = BookSerializer
    queryset = BookListView.queryset


class BookReviewsView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        book = get_object_or_404(Book, pk=self.kwargs["book_id"])
        return book.reviews.select_related("user")

    def perform_create(self, serializer):
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
    serializer_class = ReviewSerializer
    queryset = Review.objects.select_related("user")
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    http_method_names = ["patch", "delete", "options"]
