from urllib.parse import unquote

from api import serializers
from api.filters import RecipeFilter
from django.contrib.auth import update_session_auth_hash
from django.db.models import Exists, OuterRef, Value
from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from recipes.models import (Favorite, IngredientRecipe, Recipe, ShoppingList,
                            Tag)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Follow, User

from .pagination import UserPagination
from .permissions import AuthorOrReadOnly
from .utils import serializer_add_method, serializer_delete_method


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Data representation of the User model. User and subscription management.
    """
    queryset = User.objects.all()
    pagination_class = UserPagination

    def get_instance(self):
        return self.request.user

    def get_serializer_class(self):
        if self.action in ['subscriptions', 'subscribe']:
            return serializers.UserRecipesSerializer
        if self.request.method == 'GET':
            return serializers.UserGetSerializer
        return serializers.UserPostSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, ]
        return super(self.__class__, self).get_permissions()

    @action(
        detail=False,
        permission_classes=[AuthorOrReadOnly],
    )
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ['POST'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        users = User.objects.filter(
            following__user=request.user
        ).prefetch_related('recipes')
        page = self.paginate_queryset(users)

        if page is not None:
            serializer = serializers.UserRecipesSerializer(
                page, many=True,
                context={'request': request})

            return self.get_paginated_response(serializer.data)

        serializer = serializers.UserRecipesSerializer(
            users, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        follow, _ = Follow.objects.get_or_create(
            user=request.user, author=author
        )

        if request.method == 'POST':
            serializer = serializers.FollowSerializer(
                follow, context={'request': request}
            )
            return Response(serializer.data)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Representation of tag model data.
    To make changes to the model, you must use the admin panel.
    """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Data representation of the ingredient model."""
    queryset = serializers.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    pagination_class = None

    def get_queryset(self):
        """
        Redefining the ingredient object set query
        according to the query parameters.
        """
        name = self.request.query_params.get('name')
        queryset = super().get_queryset()
        if name.startswith('%'):
            name = unquote(name)
            name = name.lower()
        return queryset.filter(name__icontains=name)


class RecipeViewSet(viewsets.ModelViewSet):
    """Recipe Model Data Representation."""
    permission_classes = (AuthorOrReadOnly,)
    filterset_class = RecipeFilter
    pagination_class = UserPagination

    def get_queryset(self):
        return Recipe.objects.annotate(
            is_favorited=Exists(
                self.request.user.favorites.filter(recipe=OuterRef('pk'))
            )
            if self.request.user.is_authenticated
            else Value(False),
            is_in_shopping_cart=Exists(
                self.request.user.shopping_list.filter(recipe=OuterRef('pk'))
            )
            if self.request.user.is_authenticated
            else Value(False),
        )

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return serializers.RecipeCreateSerializer
        return serializers.RecipeReadSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        serializer = serializers.FavoriteSerializer(
            context={'request': request})
        if request.method == 'POST':
            serializer_add_method(
                serializers.FavoriteSerializer,
                request,
                pk
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer_delete_method(
            Favorite,
            request,
            pk
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        serializer = serializers.ShoppingListSerializer(
            context={'request': request})
        if request.method == 'POST':
            serializer_add_method(
                serializers.ShoppingListSerializer,
                request,
                pk
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer_delete_method(
            ShoppingList,
            request,
            pk
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['GET'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        final_list = {}
        ingredients = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount')
        for item in ingredients:
            name = item[0]
            if name not in final_list:
                final_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                final_list[name]['amount'] += item[2]
        pdfmetrics.registerFont(
            TTFont('LuckyDino', 'LuckyDino.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('LuckyDino', size=24)
        page.drawString(200, 800, 'List of ingredients')
        page.setFont('LuckyDino', size=16)
        height = 750
        for i, (name, data) in enumerate(final_list.items(), 1):
            page.drawString(75, height, (f'<{i}> {name} - {data["amount"]}, '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
