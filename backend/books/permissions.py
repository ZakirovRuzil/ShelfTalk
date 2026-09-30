"""Право доступа: изменять и удалять отзыв может только его автор."""

from rest_framework.permissions import BasePermission


class IsReviewOwner(BasePermission):
    """Разрешает object-level действие, только если request.user — автор отзыва.

    Используется в books.views.ReviewDetailView для PATCH и DELETE.
    Без исключений для staff/superuser.
    """

    message = "You can only change your own review."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
