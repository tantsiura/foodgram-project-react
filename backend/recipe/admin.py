from django.contrib import admin
from recipe.models import Tag, Recipe, Ingredient, IngredientUnits, Favorite


admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(IngredientUnits)
admin.site.register(Favorite)