from rest_framework.filters import SearchFilter

from recipes.models import Ingredient


class IngredientsFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
