from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Tag(models.Model):
    '''Model for recipe tags.'''

    name = models.CharField(
        verbose_name='Tag name',
        help_text='Tag name is unique, cannot be empty, length 200',
        max_length=200,
        unique=True,
        null=False,
    )
    slug = models.SlugField(
        verbose_name='Slug tag',
        max_length=200,
        unique=True,
        null=True,
    )
    color = models.CharField(
        verbose_name='Tag color',
        max_length=7,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


class TagImport(models.Model):
    '''Tag import model.'''
    csv_file = models.FileField(upload_to='static/data/')
    date_added = models.DateTimeField(auto_now_add=True)


class Ingredient(models.Model):
    '''Ingredient model.'''

    name = models.CharField(
        verbose_name='Ingredient',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Units',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ('name',)

    def __str__(self) -> str:
        return f'{self.name} {self.measurement_unit}'


class IngredientImport(models.Model):
    '''Ingredient import model.'''
    csv_file = models.FileField(upload_to='static/data/')
    date_added = models.DateTimeField(auto_now_add=True)


class Recipe(models.Model):
    '''Model for recipes.'''

    name = models.CharField(
        verbose_name='Name of the dish',
        max_length=200,
    )
    image = models.ImageField(
        verbose_name='Photograph of the dish',
    )
    text = models.TextField(
        verbose_name='Description of the dish',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Recipe ingredients',
        through='IngredientUnits',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Recipe tags',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking time',
        null=False,
        validators=[MinValueValidator(1.0)],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author',
        null=True,
    )
    pub_date = models.DateTimeField(
        verbose_name='Recipe publication date',
        auto_now_add=True,
        editable=False,
    )


class RecipeImport(models.Model):
    '''Recipe import model.'''
    csv_file = models.FileField(upload_to='static/data/')
    date_added = models.DateTimeField(auto_now_add=True)


class IngredientUnits(models.Model):
    '''
    Recipe relationship model with ingredients
    indicating the quantity of the latter.
    '''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Recipe Ingredients',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveIntegerField(
        verbose_name='Quantity',
    )

    class Meta:
        verbose_name = 'Recipe Ingredient'
        verbose_name_plural = 'Recipe Ingredients'
        ordering = ('recipe',)

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredient}'


class IngredientUnitsImport(models.Model):
    '''Ingredient units import model.'''
    csv_file = models.FileField(upload_to='static/data/')
    date_added = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    '''Favorite recipe model, recipe and user relationship.'''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Favorite recipe',
        related_name='favorited',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='User',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    time_saved = models.DateTimeField(
        verbose_name='Save time',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Featured Recipe'
        verbose_name_plural = 'Featured Recipes'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe',
            ),
        )
        ordering = ('time_saved',)

    def __str__(self) -> str:
        return (
            f'Users {self.user} favorite recipe(s): {self.recipe}'
        )


class ShoppingCart(models.Model):
    '''Model for shopping list.'''

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Recipe',
    )

    class Meta:
        verbose_name = 'Shopping list'
        verbose_name_plural = 'Shopping list'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} added "{self.recipe}" to his shopping list'
