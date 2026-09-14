from rest_framework.permissions import BasePermission


class IsReviewOwner(BasePermission):
    message = "You can only change your own review."

    def has_object_permission(self, request, view, obj):
        return obj.user_id == request.user.id
