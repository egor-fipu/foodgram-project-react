from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient, IngredientForRecipe, Purchase,
                     Recipe, Tag)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadyRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'name', 'image',
            'text', 'image', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_ingredients(self, obj):
        return RecipeIngredientsSerializer(
            IngredientForRecipe.objects.filter(recipe=obj), many=True
        ).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            False if not request or request.user.is_anonymous else
            Favorite.objects.filter(recipe=obj, user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            False if not request or request.user.is_anonymous else
            Purchase.objects.filter(recipe=obj, user=request.user).exists()
        )


class FavouriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Favorite.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в избранное!')
        return data

    def to_representation(self, instance):
        return ReadyRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class PurchaseSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Purchase
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe_id = data['recipe'].id
        if Purchase.objects.filter(user=user, recipe__id=recipe_id).exists():
            raise ValidationError('Рецепт уже добавлен в список покупок')
        return data

    def to_representation(self, instance):
        return ReadyRecipeSerializer(
            instance.recipe,
            context={
                'request': self.context.get('request')
            }
        ).data


class CreateIngredientsForRecipeSerializers(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientForRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(), read_only=True
    )
    ingredients = CreateIngredientsForRecipeSerializers(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    cooking_time = serializers.IntegerField(
        validators=(MinValueValidator(1, 'Время не может быть меньше 1'),)
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients',
            'tags', 'image', 'name',
            'text', 'cooking_time')

    @staticmethod
    def create_ingredients(ingredients, recipe):
        for ingredient in ingredients:
            IngredientForRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )

    @staticmethod
    def create_tags(tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = []
        tags = self.initial_data.get('tags')
        tags_list = []
        if not ingredients:
            raise ValidationError('Не выбраны ингредиенты')
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError(
                    f'{ingredient} указано не допустимое кол-во ингредиентов :'
                    f'{ingredient["amount"]}'
                )
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться'
                )
            ingredients_list.append(ingredient['id'])
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError(
                    'Теги не должны повторяться'
                )
            tags_list.append(tag)
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientForRecipe.objects.filter(recipe=instance).all().delete()
        self.create_tags(validated_data.pop('tags'), instance)
        self.create_ingredients(validated_data.pop('ingredients'), instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadyRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
