from django.contrib import admin
from recipe.models import Favorite, Ingredient, IngredientUnits, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientUnits)
admin.site.register(Favorite)
