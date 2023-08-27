from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Ingredient

from .filters import IngredientsFilter
from .permissions import AdminOrReadOnly
from .serializers import IngredientsSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (IngredientsFilter, )
    search_fields = ('^name', )
    pagination_class = None
