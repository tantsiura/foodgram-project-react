from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """The Ingredient model."""
    name = models.CharField(max_length=200,
                            verbose_name='Ingredient name')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Unit')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag model."""
    BLUE = '#0000FF'
    ORANGE = '#FFA500'
    GREEN = '#008000'
    PURPLE = '#800080'
    YELLOW = '#FFFF00'

    COLOR_CHOICES = [
        (BLUE, 'Blue'),
        (ORANGE, 'Orange'),
        (GREEN, 'Green'),
        (PURPLE, 'Violet'),
        (YELLOW, 'Yellow'),
    ]
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Tag name')
    color = models.CharField(max_length=7, unique=True, choices=COLOR_CHOICES,
                             verbose_name='Color in HEX')
    slug = models.SlugField(max_length=200, unique=True,
                            verbose_name='Unique Slug')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """The Recipe Model."""
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='recipes',
                               verbose_name='Recipe Author')
    name = models.CharField(max_length=200,
                            verbose_name='Recipe name')
    image = models.ImageField(upload_to='recipes/',
                              verbose_name='Recipe picture')
    text = models.TextField(verbose_name='Recipe Description')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ingredients',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Tags',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(
                1, message='Minimum cooking time 1 minute'),),
        verbose_name='Cooking time')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'


class IngredientAmount(models.Model):
    """The Ingredient measurement model."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ingredient',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            validators.MinValueValidator(
                1, message='Minimum number of ingredients 1'),),
        verbose_name='Quantity',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Ingredient quantity'
        verbose_name_plural = 'Quantity of ingredients'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique ingredients recipe')
        ]


class Favorite(models.Model):
    """The Model for adding a recipe to favorites."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorite recipe for user')
        ]


class Cart(models.Model):
    """The Model for adding ingredients from a recipe to the cart."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='User',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Recipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Cart'
        verbose_name_plural = 'In the cart'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique cart user')
        ]
