from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientForRecipe, Purchase,
                     Recipe, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)
    search_fields = ('name',)
    empty_value_display = '-NONE-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-NONE-'


class IngredientForRecipeInLine(admin.TabularInline):
    model = IngredientForRecipe
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'is_favorited')
    search_fields = ('name', 'author', 'tags')
    inlines = (IngredientForRecipeInLine, )
    empty_value_display = '-NONE-'

    def is_favorited(self, obj):
        return obj.is_favorited.all().count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('recipe', )
    empty_value_display = '-NONE-'


@admin.register(Purchase)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    search_fields = ('recipe', )
    empty_value_display = '-NONE-'
