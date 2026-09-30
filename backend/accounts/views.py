"""Вьюхи аутентификации: регистрация и текущий пользователь.

Логин, refresh и выдача JWT реализованы стандартными вьюхами
djangorestframework-simplejwt и подключены прямо в accounts/urls.py, без
собственного кода.
"""

from django.db import IntegrityError, transaction
from rest_framework import generics, permissions, serializers

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """`POST /api/auth/register/` — создаёт нового пользователя.

    Доступна без авторизации и не требует токена. Не выдаёт JWT — после
    регистрации клиент должен отдельно вызвать `/auth/login/`.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def perform_create(self, serializer):
        """Сохраняет пользователя в транзакции и превращает гонку по email в 400.

        RegisterSerializer.validate_email уже проверяет уникальность email,
        но между этой проверкой и записью в БД теоретически может
        вклиниться параллельный запрос с тем же email. UniqueConstraint в
        accounts.models.User — последний рубеж защиты; IntegrityError от
        него превращается здесь в обычную ошибку валидации 400, а не в 500.
        """
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {"email": ["A user with this email already exists."]}
            )


class CurrentUserView(generics.RetrieveAPIView):
    """`GET /api/auth/me/` — профиль пользователя, чей JWT передан в запросе."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
