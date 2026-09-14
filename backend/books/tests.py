from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase

from .models import Book, Review


class BookReviewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("reader@example.com", "A-good-book-2026!", display_name="Reader")
        cls.other = get_user_model().objects.create_user("other@example.com", "A-good-book-2026!", display_name="Other")
        cls.book = Book.objects.create(title="1984", author="George Orwell", publication_year=1949)

    def setUp(self):
        self.url = f"/api/books/{self.book.pk}/reviews/"
        self.data = {"rating": 8, "text": "I really enjoyed this book."}

    def make_review(self):
        return Review.objects.create(user=self.user, book=self.book, **self.data)

    def test_books_and_detail_are_public(self):
        response = self.client.get("/api/books/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        detail = self.client.get(f"/api/books/{self.book.pk}/")
        self.assertEqual(detail.status_code, 200)
        self.assertIsNone(detail.data["average_rating"])
        self.assertEqual(detail.data["reviews_count"], 0)

    def test_public_reviews_hide_email(self):
        self.make_review()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["author"], {"id": self.user.pk, "display_name": "Reader"})

    def test_guest_cannot_create_edit_or_delete_review(self):
        review = self.make_review()
        self.assertEqual(self.client.post(self.url, self.data).status_code, 401)
        self.assertEqual(self.client.patch(f"/api/reviews/{review.pk}/", self.data).status_code, 401)
        self.assertEqual(self.client.delete(f"/api/reviews/{review.pk}/").status_code, 401)

    def test_create_review_ignores_forged_author_and_book(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {**self.data, "user": self.other.pk, "book": 999})
        self.assertEqual(response.status_code, 201)
        review = Review.objects.get()
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.book, self.book)

    def test_duplicate_review_is_rejected(self):
        self.make_review()
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(self.url, self.data).status_code, 400)
        self.assertEqual(Review.objects.count(), 1)

    def test_duplicate_review_is_rejected_by_database(self):
        self.make_review()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_review()

    def test_owner_can_edit_review(self):
        review = self.make_review()
        self.client.force_authenticate(self.user)
        response = self.client.patch(f"/api/reviews/{review.pk}/", {"rating": 10, "text": "Even better on rereading.", "user": self.other.pk})
        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.rating, 10)
        self.assertEqual(review.text, "Even better on rereading.")
        self.assertEqual(review.user, self.user)

    def test_other_user_cannot_edit_review(self):
        review = self.make_review()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f"/api/reviews/{review.pk}/", {"rating": 2}).status_code, 403)
        review.refresh_from_db()
        self.assertEqual(review.rating, 8)

    def test_owner_can_delete_review(self):
        review = self.make_review()
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.delete(f"/api/reviews/{review.pk}/").status_code, 204)
        self.assertFalse(Review.objects.exists())

    def test_other_user_cannot_delete_review(self):
        review = self.make_review()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f"/api/reviews/{review.pk}/").status_code, 403)
        self.assertTrue(Review.objects.exists())

    def test_invalid_ratings_and_empty_text_are_rejected_on_create_and_edit(self):
        self.client.force_authenticate(self.user)
        for rating in (0, 11, -1, 1.5, "invalid"):
            self.assertEqual(self.client.post(self.url, {**self.data, "rating": rating}).status_code, 400)
        self.assertEqual(self.client.post(self.url, {"rating": 8, "text": " "}).status_code, 400)
        review = self.make_review()
        for changes in ({"rating": 0}, {"rating": 11}, {"text": " "}):
            self.assertEqual(self.client.patch(f"/api/reviews/{review.pk}/", changes).status_code, 400)

    def test_rating_constraint_in_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.create(user=self.user, book=self.book, rating=11, text="Invalid")

    def test_aggregates_reflect_reviews(self):
        self.make_review()
        other = Review.objects.create(user=self.other, book=self.book, rating=5, text="Interesting.")
        response = self.client.get(f"/api/books/{self.book.pk}/")
        self.assertEqual(response.data["average_rating"], 6.5)
        self.assertEqual(response.data["reviews_count"], 2)
        other.delete()
        self.assertEqual(self.client.get(f"/api/books/{self.book.pk}/").data["average_rating"], 8)

    def test_books_cannot_be_changed_via_api(self):
        for user in (self.user, self.other):
            self.client.force_authenticate(user)
            self.assertEqual(self.client.post("/api/books/", {"title": "New", "author": "Me"}).status_code, 405)
            self.assertEqual(self.client.patch(f"/api/books/{self.book.pk}/", {"title": "Changed"}).status_code, 405)
            self.assertEqual(self.client.delete(f"/api/books/{self.book.pk}/").status_code, 405)

    def test_missing_book_and_review_return_404(self):
        self.assertEqual(self.client.get("/api/books/99999/").status_code, 404)
        self.assertEqual(self.client.get("/api/books/99999/reviews/").status_code, 404)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post("/api/books/99999/reviews/", self.data).status_code, 404)
        self.assertEqual(self.client.patch("/api/reviews/99999/", self.data).status_code, 404)

    def test_seed_is_repeatable_and_preserves_edits(self):
        call_command("seed_books", stdout=StringIO())
        self.book.description = "Administrator's description"
        self.book.save()
        call_command("seed_books", stdout=StringIO())
        self.assertEqual(Book.objects.count(), 8)
        self.book.refresh_from_db()
        self.assertEqual(self.book.description, "Administrator's description")
