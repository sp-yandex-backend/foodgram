from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscribe, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color", "slug"]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit"]


class IngredientRecipeReadSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit", "amount"]

    def get_amount(self, obj):
        return IngredientRecipe.objects.get(
            recipe=self.context["recipe"], ingredient=obj
        ).amount


class IngredientRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(), slug_field="id"
    )

    class Meta:
        model = IngredientRecipe
        fields = ["id", "amount", "recipe"]


class IngredientRecipeCreateSerializer(serializers.ModelSerializer):
    ingredient = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(),
        slug_field="id",
    )

    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(), slug_field="id"
    )

    class Meta:
        model = IngredientRecipe
        fields = ["ingredient", "amount", "recipe"]


class AuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        ]

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Subscribe.objects.filter(user=obj, following=user).exists()
        return False


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    author = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "tags",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
            "author",
        ]

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=self.context["request"].user, recipe=obj
            ).exists()
        return False

    def get_author(self, obj):
        return AuthorSerializer(
            instance=obj.author, context={"request": self.context["request"]}
        ).data

    def get_ingredients(self, obj):
        return IngredientRecipeReadSerializer(
            instance=obj.ingredients, many=True, context={"recipe": obj}
        ).data


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    tags = (
        serializers.SlugRelatedField(
            queryset=Tag.objects.all(), many=True, slug_field="id"
        ),
    )
    ingredients = IngredientRecipeWriteSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "author",
        ]


class SubscribeRequestSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="id",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    following = serializers.SlugRelatedField(
        slug_field="id", queryset=User.objects.all()
    )

    class Meta:
        model = Subscribe
        fields = ["user", "following"]
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(), fields=["user", "following"]
            )
        ]

    def validate(self, data):
        if self.context["request"].user != data.get("following"):
            return data
        raise serializers.ValidationError("Can't sign for yourself")


class SubscribeResponseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = RecipeReadSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        ]

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(
            user=self.context["request"].user, following=obj
        ).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteRequestSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="id",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.SlugRelatedField(
        slug_field="id", queryset=Recipe.objects.all()
    )

    class Meta:
        model = Favorite
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=["user", "recipe"]
            )
        ]


class FavoriteResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]


class ShoppingCartRequestSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="id",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.SlugRelatedField(
        slug_field="id", queryset=Recipe.objects.all()
    )

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(), fields=["user", "recipe"]
            )
        ]


class ShoppingCartResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
        ]
