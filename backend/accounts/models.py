"""Кастомная модель пользователя: вход по email вместо username."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower

from .managers import UserManager


class User(AbstractUser):
    """Пользователь ShelfTalk.

    Наследует стандартные поля Django (пароль, права, флаги is_staff и
    т.д.) из AbstractUser, но убирает username и делает email
    единственным способом входа. Уникальность email обеспечена без учёта
    регистра — и на уровне БД (UniqueConstraint по Lower(email)), и в
    сериализаторе (accounts.serializers.RegisterSerializer), который
    отдельно проверяет это перед сохранением, чтобы вернуть аккуратную
    ошибку 400 вместо IntegrityError.
    """

    username = None
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=80)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"), name="unique_email_case_insensitive"
            ),
        ]

    def save(self, *args, **kwargs):
        """Нормализует email (нижний регистр) перед каждым сохранением.

        Страхует случаи, когда объект создан или изменён в обход
        UserManager.create_user — например, через Django Admin.
        """
        self.email = UserManager.normalize_email(self.email)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
