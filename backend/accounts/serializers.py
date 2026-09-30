"""Сериализаторы для регистрации, логина и просмотра профиля."""

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Публичное представление пользователя (ответ `/auth/me/`).

    Пароль сюда намеренно не входит.
    """

    class Meta:
        model = User
        fields = ("id", "email", "display_name", "first_name", "last_name")


class RegisterSerializer(serializers.ModelSerializer):
    """Валидация и создание нового пользователя (`POST /auth/register/`)."""

    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("id", "email", "display_name", "first_name", "last_name", "password")

    def validate_email(self, value):
        """Отклоняет email, уже занятый другим пользователем (без учёта регистра).

        Raises:
            serializers.ValidationError: если такой email уже зарегистрирован.
        """
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, attrs):
        """Прогоняет пароль через стандартные валидаторы Django.

        Список валидаторов задан в AUTH_PASSWORD_VALIDATORS
        (config/settings.py): проверка на схожесть с данными
        пользователя, минимальную длину, вхождение в список
        распространённых паролей и на то, что пароль не состоит только
        из цифр.

        Raises:
            serializers.ValidationError: с текстом ошибок Django под
                ключом "password", если пароль не прошёл проверку.
        """
        user = User(**{key: value for key, value in attrs.items() if key != "password"})
        try:
            validate_password(attrs["password"], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages})
        return attrs

    def create(self, validated_data):
        """Создаёт пользователя через UserManager, чтобы пароль был захеширован."""
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    """Логин по email/паролю с выдачей пары JWT-токенов.

    Наследует стандартную логику djangorestframework-simplejwt и только
    приводит присланный email к тому же нормализованному виду, в котором
    он хранится в БД, — иначе логин с другим регистром email не найдёт
    пользователя.
    """

    def validate(self, attrs):
        attrs["email"] = User.objects.normalize_email(attrs["email"])
        return super().validate(attrs)
