from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.pagination import LimitPageNumberPagination
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import AdminOrAuthor, AdminOrReadOnly
from api.serializers import (CustomUserSerializer, IngridientsSerializer,
                             RecipeFavoriteAndShopping, RecipeSerializerRead,
                             RecipeSerializerWrite, SubscribeSerializer,
                             TagSerializer)
from recipe.models import (Favorite, Ingredient, IngredientUnits, Recipe,
                           ShoppingCart, Tag)
from users.models import Subscribe

User = get_user_model()


class UsersViewSet(UserViewSet):
    '''Viewset for user models.'''
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    search_fields = ('username', 'email')
    permission_classes = (AllowAny, )

    def subscribed(self, serializer, id=None):
        subscriptioner = get_object_or_404(User, id=id)
        if self.request.user == subscriptioner:
            return Response({'message': 'You cannot follow yourself'},
                            status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscribe.objects.get_or_create(user=self.request.user,
                                                       author=subscriptioner)
        serializer = SubscribeSerializer(subscription[0])
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribed(self, serializer, id=None):
        subscriptioner = get_object_or_404(User, id=id)
        Subscribe.objects.filter(user=self.request.user,
                                 author=subscriptioner).delete()
        return Response({'message': 'You have successfully unsubscribed'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, serializer, id):
        if self.request.method == 'DELETE':
            return self.unsubscribed(serializer, id)
        return self.subscribed(serializer, id)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, serializer):
        subscriptioning = Subscribe.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(subscriptioning)
        serializer = SubscribeSerializer(pages, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngridientsSerializer
    permission_classes = (AdminOrReadOnly,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminOrAuthor,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPagination

    def get_serializer_class(self):
        if self.action in (
            'list',
            'retrieve',
        ):
            return RecipeSerializerRead
        return RecipeSerializerWrite

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.save(Favorite, request.user, pk)
        else:
            return self.remove(Favorite, request.user, pk)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.save(ShoppingCart, request.user, pk)
        else:
            return self.remove(ShoppingCart, request.user, pk)

    def save(self, model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({'errors': 'The recipe has been added!'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        obj = model.objects.create(user=user, recipe=recipe)
        serializer = RecipeFavoriteAndShopping(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove(self, model, user, pk):
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response({'message':
                             'The recipe has been successfully deleted.'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'The recipe has been deleted!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            IngredientUnits.objects.filter(recipe__in_shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        data = ingredients.values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'total_amount'
        )
        shopping_cart = 'Shopping list:\n'
        for name, measure, amount in data:
            shopping_cart += f'{name.capitalize()} {amount} {measure},\n'

        return HttpResponse(shopping_cart, content_type='text/plain')
