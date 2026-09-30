"""Регистрация модели User в Django Admin с формами под email-логин."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя в админке: email вместо username."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "display_name")


class CustomUserChangeForm(UserChangeForm):
    """Форма редактирования пользователя в админке без поля username."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Настройка стандартного UserAdmin под кастомную модель User."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ("email", "display_name", "is_staff", "is_active")
    search_fields = ("email", "display_name")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("display_name", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "display_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
