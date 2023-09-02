from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (DummyUserSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeSimpleSerializer,
                             RecipeWriteSerializer, TagSerializer,
                             UserCreateSerializer, UserSerializer,
                             UserWithRecipesSerializer,
                             UserWSubscriptionSerializer)
from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as BaseUserViewSet
from recipes.models import Favorite as FavoriteModel
from recipes.models import Ingredient as IngredientModel
from recipes.models import IngredientRecipe as IngredientRecipeModel
from recipes.models import Recipe as RecipeModel
from recipes.models import ShoppingСart as ShoppingСartModel
from recipes.models import Tag as TagModel
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

UserModel = get_user_model()


class UserViewSet(BaseUserViewSet):
    '''ViewSet for Users'''
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

    def _get_subs_context(self):
        context = self.get_serializer_context()
        context['recipes_limit'] = self.request.query_params.get(
            'recipes_limit', None
        )
        return context

    def get_serializer_class(self):
        if self.action == 'subscribe':
            return DummyUserSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('list', 'retrieve'):
            return UserWSubscriptionSerializer
        return super().get_serializer_class()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, *args, **kwargs):
        '''Subscription Management - Adding and Removing.'''
        author_id = kwargs['id']
        data = dict(request.data)
        data.update(kwargs)

        try:
            author = UserModel.objects.get(pk=author_id)
        except UserModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            affected, _ = author.following.filter(user=request.user).delete()
            if not affected:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'There is no such subscription.',
                })

            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'POST':
            if request.user.pk == author.pk:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'You cannot subscribe to yourself',
                })

            if author.following.filter(user=request.user).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'You are already subscribed to this author',
                })

            author.following.create(user=request.user)

            subs_context = self._get_subs_context()
            queryset = self.get_queryset()
            queryset = queryset.filter(following__user=self.request.user)
            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = UserWithRecipesSerializer(
                    page, many=True, context=subs_context
                )
                response = self.get_paginated_response(serializer.data)
                response.status = status.HTTP_201_CREATED
                return response

            serializer = UserWithRecipesSerializer(
                queryset, many=True, context=subs_context
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request, *args, **kwargs):
        '''Getting a list of subscriptions.'''
        context = self._get_subs_context()
        queryset = self.get_queryset()
        queryset = queryset.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True, context=context
            )
            return self.get_paginated_response(serializer.data)

        queryset = queryset.all()
        serializer = UserWithRecipesSerializer(
            instance=queryset, many=True, context=context
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(ReadOnlyModelViewSet):
    '''ViewSet for Tags.'''
    queryset = TagModel.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    '''ViewSet for Ingredients.'''
    queryset = IngredientModel.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    '''ViewSet for Recipes. '''
    queryset = RecipeModel.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        write_serializer = RecipeWriteSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        self.perform_create(write_serializer)

        read_serializer = self.get_serializer(
            instance=write_serializer.instance
        )
        headers = self.get_success_headers(data=read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        write_serializer = RecipeWriteSerializer(
            instance=instance, data=request.data,
            context=self.get_serializer_context(),
            partial=partial
        )
        write_serializer.is_valid(raise_exception=True)
        self.perform_update(write_serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        read_serializer = self.get_serializer(
            instance=write_serializer.instance
        )
        headers = self.get_success_headers(data=read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, *args, **kwargs):
        '''Adding and deleting a recipe to favorites.'''
        recipe_id = kwargs['pk']

        try:
            recipe = RecipeModel.objects.get(pk=recipe_id)
        except RecipeModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            query = FavoriteModel.objects.filter(
                user=request.user,
                recipe=recipe,
            )
            affected, _ = query.delete()
            if not affected:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'There is no such favorite recipe.',
                })

            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'POST':
            _, created = FavoriteModel.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

            if not created:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'errors':
                        'The recipe is already in the list of favorites.',
                    }
                )

            serializer = RecipeSimpleSerializer(
                instance=recipe, context=self.get_serializer_context(),
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, *args, **kwargs):
        '''Adding and Removing Recipes to the Cart.'''
        recipe_id = kwargs['pk']

        try:
            recipe = RecipeModel.objects.get(pk=recipe_id)
        except RecipeModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'DELETE':
            query = ShoppingСartModel.objects.filter(
                user=request.user,
                recipe=recipe,
            )
            affected, _ = query.delete()
            if not affected:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'There is no such favorite recipe.',
                })

            return Response(status=status.HTTP_204_NO_CONTENT)

        if request.method == 'POST':
            _, created = ShoppingСartModel.objects.get_or_create(
                user=request.user,
                recipe=recipe
            )

            if not created:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                    'errors': 'The recipe is already in the cart.',
                })

            serializer = RecipeSimpleSerializer(
                instance=recipe, context=self.get_serializer_context(),
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, *args, **kwargs):
        """ Получение корзины для покупок """
        items = IngredientRecipeModel.objects.select_related(
            'recipe', 'ingredient'
        )
        if request.user.is_authenticated:
            items = items.filter(
                recipe__shopping_cart__user=request.user
            )
        else:
            items = items.filter(
                recipe_id__in=request.session['purchases']
            )

        items = items.values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            name=F('ingredient__name'),
            units=F('ingredient__measurement_unit'),
            total=Sum('amount'),
        ).order_by('-total')

        text = '\n'.join([
            f"{item['name']} ({item['units']}) - {item['total']}"
            for item in items
        ])
        filename = "foodgram_shopping_cart.txt"
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename{filename}'

        return response
