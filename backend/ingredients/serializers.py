from recipes.models import Ingredient, IngredientsAmount
from rest_framework import serializers
from rest_framework.fields import IntegerField


class IngredientsSerializer(serializers.ModelSerializer):
    '''Ingredient serializer.'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )


class IngredientUnitsSerializers(serializers.ModelSerializer):
    '''A serializer for the quantity of ingredients for a recipe.'''

    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientsAmount
        fields = (
            'id',
            'amount',
        )
