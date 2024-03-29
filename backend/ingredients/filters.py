from recipes.models import Ingredient
from rest_framework.filters import SearchFilter


class IngredientsFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)
