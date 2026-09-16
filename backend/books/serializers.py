from rest_framework import serializers

from accounts.models import User

from .models import Book, Review


class BookSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = User
        fields = ("id", "display_name")


class ReviewSerializer(serializers.ModelSerializer):
    author = ReviewAuthorSerializer(source="user", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "rating", "text", "author", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
