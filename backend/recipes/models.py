from django.contrib.auth import get_user_model
from django.core import validators
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    """Tag Model."""

    name = models.CharField(
        max_length=200,
        verbose_name='Tag'
    )
    color = models.CharField(
        unique=True,
        max_length=7,
        help_text='Enter color in RGB format (#rrggbb)',
        validators=[
            validators.RegexValidator(
                r'^#[a-fA-F0-9]{6}$',
                'Use RGB Format to Specify Color (#AABBCC)',
            )
        ],
    )
    slug = models.SlugField(
        verbose_name='Slug name',
        help_text='Enter the name of the slug',
        unique=True,
        max_length=200,
    )

    class Meta:
        ordering = ('id',)
        verbose_name_plural = 'Tags'
        default_related_name = 'tags'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    """Ingredients Model"""

    name = models.CharField(
        max_length=200,
        verbose_name='Ingredient name'
    )
    measurement_unit = models.CharField(
        verbose_name='Unit',
        help_text='Enter the unit of measure for the ingredient.',
        max_length=200,
    )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Ingredients'
        indexes = [
            models.Index(fields=['name'], name='name_index'),
        ]


class Recipe(models.Model):
    """Recipe model."""

    name = models.CharField(
        max_length=200,
        help_text='Enter recipe name'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date',
        help_text='Enter the publication date of the recipe',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Recipe Author',
        help_text='Enter the author of the recipe',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Description of cooking',
        help_text='Enter a description of the preparation of the dish',
    )
    tags = models.ManyToManyField(Tag, related_name='tags')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='ingredients',
    )
    image = models.ImageField(
        verbose_name='Image',
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking time (in minutes)',
        help_text='Enter cooking time in minutes',
        validators=[
            MinValueValidator(
                1,
                message='Specify a time greater than or equal to 1'
            ),
        ],
    )

    def __str__(self) -> str:
        return f'id: {self.id} Author: {str(self.author)} Name: {self.name}'

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_for_author',
            ),
        )


class IngredientRecipe(models.Model):
    """A model for linking a recipe and its corresponding ingredients."""

    name = models.CharField(
        'Title',
        max_length=200,
        help_text='Enter the title',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient_list',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Enter the amount of ingredients',
        validators=[
            MinValueValidator(
                1,
                message='Enter a quantity greater than or equal to 1'
            ),
        ],
    )

    def __str__(self):
        return f'{self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'Ingredient in the recipe'
        verbose_name_plural = 'Recipe Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            )
        ]


class FavoritesAndShopping(models.Model):
    """
    Model for generating the inherited Favorite and ShoppingList models.
    """

    user = models.ForeignKey(
        User, verbose_name='User', on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe, verbose_name='Recipe', on_delete=models.CASCADE
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(FavoritesAndShopping):
    """Favorite Recipes"""

    class Meta(FavoritesAndShopping.Meta):
        verbose_name = 'Favorite Recipe'
        verbose_name_plural = 'Favorite Recipes'
        default_related_name = 'favorites'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingList(FavoritesAndShopping):
    """Recipes added to shopping list."""

    class Meta(FavoritesAndShopping.Meta):
        verbose_name = 'Recipe on shopping list'
        verbose_name_plural = 'Recipes in the shopping list'
        default_related_name = 'shopping_list'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
