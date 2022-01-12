from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('tags', views.TagsViewSet, basename='tags')
router.register(
    'ingredients', views.IngredientsViewSet, basename='ingredients'
)
router.register('recipes', views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls))
]
