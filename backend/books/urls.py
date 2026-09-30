"""Маршруты каталога, подключённые в config/urls.py под /api/."""

from django.urls import path

from .views import BookDetailView, BookListView, BookReviewsView, ReviewDetailView

urlpatterns = [
    path("books/", BookListView.as_view()),
    path("books/<int:pk>/", BookDetailView.as_view()),
    path("books/<int:book_id>/reviews/", BookReviewsView.as_view()),
    path("reviews/<int:pk>/", ReviewDetailView.as_view()),
]
