from django.apps import AppConfig


class IngredientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ingredients'
    verbose_name = 'ingredient'
    verbose_name_plural = 'ingredients'
