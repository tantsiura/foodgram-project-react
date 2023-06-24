from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Display data of the User model."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email')
    list_editable = ('password',)
    readonly_fields = ('last_login', 'date_joined',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Display model data Follow."""

    list_display = (
        'user',
        'author',
    )
