from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from foodgram.settings import MAX_EMAIL_LENGHT, MAX_LENGHT_1
from users.validators import validate_name, validate_username


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='Email',
        max_length=MAX_EMAIL_LENGHT,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Login',
        max_length=MAX_LENGHT_1,
        unique=True,
        validators=(validate_username, UnicodeUsernameValidator,),
    )
    first_name = models.CharField(
        verbose_name='Name',
        max_length=MAX_LENGHT_1,
        blank=False,
        validators=(validate_name, ),
    )
    last_name = models.CharField(
        verbose_name='Surname',
        max_length=MAX_LENGHT_1,
        blank=False,
        validators=(validate_name, ),
    )
    password = models.CharField(
        verbose_name='Password',
        max_length=MAX_LENGHT_1,
    )

    class Meta:
        ordering = ('username', )
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f'{self.username}, {self.email}'


class Follow(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Author',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Follower',
    )
    created = models.DateTimeField(
        verbose_name='Subscription date',
        auto_now_add=True
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follower')
        ]

    def __str__(self):
        return f'{self.user} - {self.author}'
