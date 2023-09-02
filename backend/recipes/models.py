from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from foodgram.settings import MAX_LENGHT_2
from users.validators import validate_name

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Name of tag',
        max_length=MAX_LENGHT_2,
        unique=True,
        validators=(validate_name,)
    )
    color = ColorField(
        verbose_name='Color',
        max_length=7,
        unique=True,
        default='#FF0000',
    )
    slug = models.SlugField(
        verbose_name='Uniqe slug',
        max_length=MAX_LENGHT_2,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Name of ingredient',
        max_length=MAX_LENGHT_2,
        validators=(validate_name, )
    )
    measurement_unit = models.CharField(
        verbose_name='Unit',
        max_length=MAX_LENGHT_2,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Athour of the recipe',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True,
    )
    name = models.CharField(
        verbose_name='Name of the recipe',
        max_length=MAX_LENGHT_2,
        validators=(validate_name, )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ingredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Тег',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Image of recipe',
        upload_to='recipes/image/',
        blank=True,
    )
    text = models.TextField(
        verbose_name='Description of the recipe',
        max_length=500,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Time of cooking',
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(600)],
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):

    tag = models.ForeignKey(
        Tag,
        verbose_name='Tags',
        on_delete=models.CASCADE,
        related_name='tag_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Recipe',
        on_delete=models.CASCADE,
        related_name='tag_recipes',
    )

    class Meta:
        verbose_name = 'Tag of the recipe'
        verbose_name_plural = 'Tags of the recipes'
        ordering = (
            'recipe__name',
            'tag__name',
        )
        unique_together = ('tag', 'recipe',)

    def __str__(self):
        return f'{self.id}: {self.recipe.name}, {self.tag.name}'


class IngredientRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='ingredientrecipes',
        on_delete=models.CASCADE,
        verbose_name='Ingredient'
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='ingredientrecipes',
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Quantity',
        default=1,
        validators=(
            MinValueValidator(
                1, 'Quantity must be at least 1.',
            ),
        ),
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Quantity of the Ingredient'
        verbose_name_plural = 'Quantity of Ingredients'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_to_ingredient_exists')]

    def __str__(self):
        return (f'{self.recipe}: {self.ingredient.name},'
                f' {self.amount}')


class FavoriteShoppingCartModel(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe',
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Favorite(FavoriteShoppingCartModel):

    class Meta:
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'
        default_related_name = 'favorite'
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorite_unique_recipe'
            )
        ]


class ShoppingСart(FavoriteShoppingCartModel):

    class Meta:
        verbose_name = 'Shopping cart'
        default_related_name = 'shopping_cart'
        constraints = [
            UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_in_shopping_cart'
            )
        ]
