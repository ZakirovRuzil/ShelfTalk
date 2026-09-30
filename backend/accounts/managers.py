"""Менеджер модели User: email вместо username как логин."""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Создаёт пользователей по email вместо стандартного username.

    Нужен, потому что accounts.models.User убирает поле username и делает
    email полем для входа (USERNAME_FIELD = "email").
    """

    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """Приводит email к нижнему регистру после стандартной нормализации Django.

        Это единственное место, где вычисляется канонический вид email —
        им же пользуются сериализаторы (accounts/serializers.py) перед
        поиском существующего пользователя, чтобы регистр не влиял на
        уникальность.
        """
        return super().normalize_email(email).strip().lower()

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт обычного пользователя с хешированным паролем.

        Args:
            email: адрес пользователя, будет нормализован.
            password: пароль в открытом виде; будет захеширован перед сохранением.
            **extra_fields: остальные поля модели User (display_name и т.д.).

        Raises:
            ValueError: если email не передан или пустой.
        """
        if not email:
            raise ValueError("Email is required.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создаёт суперпользователя (для `manage.py createsuperuser`).

        Raises:
            ValueError: если email пустой, либо явно переданы
                is_staff=False или is_superuser=False (суперпользователь
                обязан иметь оба флага).
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if not extra_fields["is_staff"] or not extra_fields["is_superuser"]:
            raise ValueError("Superuser must have is_staff=True and is_superuser=True.")
        return self.create_user(email, password, **extra_fields)
