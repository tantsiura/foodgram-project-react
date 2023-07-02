from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.customfields import LowercaseEmailField


class User(AbstractUser):
    """Customized user model."""
    email = LowercaseEmailField(
        'Email',
        unique=True,)
    first_name = models.CharField(
        verbose_name="Name", max_length=150, blank=False
    )
    last_name = models.CharField(
        verbose_name="Surname", max_length=150, blank=False
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        verbose_name="Unique username",
        max_length=150,
        unique=True,
        help_text="Max 150 characters. Letters, numbers and @/./+/-/_.",
        validators=[username_validator],
        error_messages={
            "unique": "User already exists",
        },
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        "first_name",
        "last_name",
        "password",
        "username",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "User"
        verbose_name_plural = "Users"


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        related_name="subscriber",
        verbose_name="Subscriber",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name="subscribing",
        verbose_name="Author",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            )
        ]
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
