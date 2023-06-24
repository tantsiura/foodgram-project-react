from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingList, Tag


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    """Model Data Display Favorites"""
    list_display = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Show model data for a shopping list"""
    list_display = ('user', 'recipe')


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Displaying the data of the Tag model."""

    list_display = (
        'name',
        'color',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Displaying Ingredients model data."""

    list_display = (
        'name',
        'measurement_unit',
    )

    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):
    """
    Сlass for adding ingredients to a recipe in the admin panel.
    """

    model = Recipe.ingredients.through
    extra = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    """Recipe model data display."""

    list_display = (
        'name',
        'author',
    )
    list_filter = (
        'name',
        'author',
        'tags',
    )

    readonly_fields = ('favorites_count',)

    inlines = (IngredientsInline,)

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        """
        Displays the number of times a recipe has
        been added to the favorites list by anyone.
        """
        return obj.favorites.count()
