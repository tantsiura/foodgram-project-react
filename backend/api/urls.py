from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UsersViewSet)
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UsersViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
