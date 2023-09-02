from django.contrib import admin
from django.contrib.admin import TabularInline
from django.utils.safestring import mark_safe
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingСart, Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '- empty -'


class IngredientRecipeInline(TabularInline):
    model = IngredientRecipe
    min_num = 1
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    search_fields = ('name', 'color',)
    list_filter = ('name', 'color',)
    empty_value_display = '- empty -'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'name', 'get_ingredients',
                    'get_tags', 'favorite')
    fields = ('name', 'author', 'text', 'image',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientRecipeInline,)
    empty_value_display = '- empty -'

    @admin.display(description='Image')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" hieght="30"')

    @admin.display(description='Favorite')
    def favorite(self, obj):
        return obj.favorite.count()

    @admin.display(description='Ingredients')
    def get_ingredients(self, obj):
        ingredients_list = []
        for ingredient in obj.ingredients.all():
            ingredients_list.append(ingredient.name.lower())
        return ', '.join(ingredients_list)

    @admin.display(description='Tags')
    def get_tags(self, obj):
        ls = [_.name for _ in obj.tags.all()]
        return ', '.join(ls)


@admin.register(ShoppingСart)
class ShoppingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe', )
    empty_value_display = '- empty -'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('user', 'recipe', )
    empty_value_display = '- empty -'
