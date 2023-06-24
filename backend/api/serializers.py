import base64

from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.transaction import atomic
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingList, Tag)
from rest_framework import exceptions, relations, serializers, status
from rest_framework.exceptions import ValidationError
from users.models import Follow, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, image_string = data.split(';base64,')
            file_extension = format.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_string),
                name=f'temp.{file_extension}'
            )
        return super().to_internal_value(data)


class UserGetSerializer(UserSerializer):
    """A serializer for viewing the user's profile."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False

        return Follow.objects.filter(
            author=obj, user=request.user
        ).exists()


class UserRecipesSerializer(UserGetSerializer):
    """Serializer to view user with recipes."""

    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = UserGetSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='You are already following this user!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='You cannot subscribe to yourself!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, object):
        request = self.context.get('request')
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        queryset = object.recipes.all()
        if recipes_limit:
            queryset = queryset[:int(recipes_limit)]

        return RecipeShortSerializer(queryset, context=context, many=True).data


class UserPostSerializer(UserCreateSerializer):
    """The serializer to create the user."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """Serializer for displaying summary information about recipes."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UserGetSerializer):
    """The serializer for subscriptions."""
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Follow
        fields = ('author', 'user', )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=['author', 'user', ],
                message='You are already following this user!'
            )
        ]

    @transaction.atomic
    def create(self, validated_data):
        return Follow.objects.create(
            user=self.context.get('request').user, **validated_data)

    @transaction.atomi
    def validate_author(self, value):
        if self.context.get('request').user == value:
            raise serializers.ValidationError({
                'errors': 'Subscribing to yourself is not possible!'
            })
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """The serializer for the Ingredient model."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """A serializer for displaying ingredients in recipes."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class FavoriteAndShoppingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding recipes to your favorites list and shopping cart.
    """
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
    )

    class Meta:
        abstract = True
        fields = ('user', 'recipe')


class FavoriteSerializer(FavoriteAndShoppingCreateSerializer):
    """Serializer for adding recipes to favorites."""

    class Meta(FavoriteAndShoppingCreateSerializer.Meta):
        model = Favorite
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user', ],
                message='This recipe has already been added to favorites.'
            )
        ]

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context.get('request').user, **validated_data
        )


class ShoppingListSerializer(FavoriteAndShoppingCreateSerializer):
    """A serializer for creating a shopping list."""

    class Meta(FavoriteAndShoppingCreateSerializer.Meta):
        model = ShoppingList
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=['recipe', 'user', ],
                message='''
                This recipe has already been added to the shopping list.
                '''
            )
        ]

    def create(self, validated_data):
        return self.Meta.model.objects.create(
            user=self.context.get('request').user, **validated_data
        )


class TagSerializer(serializers.ModelSerializer):
    """The serializer for the Tag model."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeReadSerializer(serializers.ModelSerializer):
    """
    Define serialization logic for reading (displaying) recipe model objects.
    """

    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserGetSerializer(read_only=True)
    is_favorited = serializers.BooleanField(default=False, read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        default=False, read_only=True
    )
    ingredients = IngredientRecipeSerializer(
        many=True, read_only=True, source='ingredient_list'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """A serializer for creating recipes."""

    tags = relations.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    @atomic
    def create_bulk_ingredients(self, ingredients, recipe):
        ingredients_list = []
        for ingredient in ingredients:
            current_ingredient = ingredient['ingredient']['id']
            current_amount = ingredient.get('amount')
            ingredients_list.append(
                IngredientRecipe(
                    recipe=recipe,
                    ingredient=current_ingredient,
                    amount=current_amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredients_list)

    @atomic
    def create(self, validated_data):
        try:
            ingredients_list = validated_data.pop('ingredients')
            tags = validated_data.pop('tags')
            author = self.context.get('request').user
            recipe = Recipe.objects.create(author=author, **validated_data)
            recipe.save()
            recipe.tags.set(tags)
            self.create_bulk_ingredients(ingredients_list, recipe)
            return recipe
        except IntegrityError:
            error_message = (
                'The name of the recipe with the given name already exists!'
            )
            raise serializers.ValidationError({'error': error_message})

    @atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_bulk_ingredients(recipe=instance, ingredients=ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        )
        return serializer.data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise exceptions.ValidationError(
                {'ingredients': '''
                It is impossible to add a recipe without ingredients!
                '''}
            )
        ingredients_list = []
        for item in ingredients:
            if item['id'] in ingredients_list:
                raise exceptions.ValidationError(
                    {'ingredients': 'Ingredients cannot be repeated!'}
                )
            ingredients_list.append(item['id'])
            if int(item['amount']) < 1:
                raise exceptions.ValidationError(
                    {
                        'amount': (
                            'The number of ingredients cannot be less than 1!'
                        )
                    }
                )
        return data

    def validate_cooking_time(self, data):
        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError(
                {'cooking_time': (
                    '''
                    The cooking time of a recipe cannot be less than
                     or equal to 0!
                    '''
                )}
            )
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags', False)
        if not tags:
            raise exceptions.ValidationError(
                {'tags': 'A recipe cannot be created without tags!'}
            )
        tags_list = []
        for tags in tags:
            if tags in tags_list:
                raise exceptions.ValidationError(
                    {'tags': 'Do not use duplicate tags!'}
                )
            tags_list.append(tags)
        return data
