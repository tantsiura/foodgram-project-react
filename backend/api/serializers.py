import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_list_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipe.models import Ingredient, IngredientUnits, Recipe, Tag
from rest_framework import serializers
from rest_framework.fields import IntegerField
from users.models import Subscribe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
        )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

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
        if self.context.get('request') and (
                not self.context['request'].user.is_anonymous):
            user = self.context.get('request').user
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    '''Data serializer for recipe tags.'''

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'slug',
            'color',
        )


class IngridientsSerializer(serializers.ModelSerializer):
    '''Ingredient serializer.'''

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientUnitsSerializers(serializers.ModelSerializer):
    '''A serializer for the quantity of ingredients for a recipe.'''

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientUnits
        fields = (
            'id',
            'amount',
        )


class RecipeSerializerRead(serializers.ModelSerializer):
    '''Recipe serializer for retrieve and list actions.'''

    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True,
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

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (obj.favorited.filter(user=request.user).exists()
                and not request.user.is_anonymous) or None

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (obj.in_shopping_cart.filter(user=request.user).exists()
                and not request.user.is_anonymous) or None

    def get_ingredients(self, obj):
        return (obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientunits__amount'),
        ))


class RecipeSerializerWrite(serializers.ModelSerializer):
    '''Recipe serializer for writing data.'''

    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientUnitsSerializers(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        ingredients_list = list()

        for ingredient in ingredients_data:
            ingredients_list.append(
                IngredientUnits(
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    recipe=recipe,
                    amount=ingredient['amount'])
            )
        IngredientUnits.objects.bulk_create(ingredients_list)
        recipe.tags.set(tags_data)
        return recipe

    def update(self, recipe, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        IngredientUnits.objects.filter(recipe=recipe).delete()
        for ingredient in ingredients_data:
            IngredientUnits.objects.create(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'],
            )
        recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializerRead(instance, context=context).data


class RecipeFavoriteAndShopping(serializers.ModelSerializer):
    '''Recipe serializer for favorites and shopping list.'''

    id = serializers.IntegerField(source='recipe.id')
    name = serializers.CharField(source='recipe.name')
    image = serializers.ImageField(source='recipe.image')
    cooking_time = serializers.IntegerField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeSubsribe(serializers.ModelSerializer):
    '''Recipe serializer for subscriptions.'''
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = serializers.ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscribeSerializer(serializers.ModelSerializer):
    '''The serializer for subscriptions.'''
    recipes = serializers.SerializerMethodField()

    id = serializers.IntegerField(source='author.id')
    email = serializers.EmailField(source='author.email')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    recipes_count = serializers.SerializerMethodField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        '''Returns a list of recipes in subscriptions.'''
        recipes = get_list_or_404(Recipe, author=obj.author)
        serializer = RecipeSubsribe(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(user=obj.user,
                                        author=obj.author).exists()
