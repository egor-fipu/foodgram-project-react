from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import Recipe
from .models import Follow

User = get_user_model()


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=self.context['request'].user,
            following=obj
        ).exists()


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    following = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        author = data['following'].id
        user = data['user']
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя'
            )
        if Follow.objects.filter(following__id=author, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя'
            )
        return data


class FollowingRecipesSerializers(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ReadyFollowSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed',
            'recipes', 'recipes_count')
        read_only_fields = fields

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return data.follower.filter(user=data, following=request.user).exists()

    def get_recipes(self, data):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = (data.recipes.all()[:int(limit)] if limit else
                   data.recipes.all())
        context = {'request': request}
        return FollowingRecipesSerializers(
            recipes, many=True, context=context
        ).data

    def get_recipes_count(self, data):
        return data.recipes.count()
