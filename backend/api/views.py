from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscribe, Tag, TagRecipe)
from .serializers import (FavoriteRequestSerializer,
                          FavoriteResponseSerializer,
                          IngredientRecipeCreateSerializer,
                          IngredientSerializer, RecipeReadSerializer,
                          RecipeWriteSerializer, ShoppingCartRequestSerializer,
                          ShoppingCartResponseSerializer,
                          SubscribeRequestSerializer,
                          SubscribeResponseSerializer, TagSerializer)


class TagView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return Ingredient.objects.filter(name__startswith=name)
        return Ingredient.objects.all()


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["author", ]
    ordering = "-pub_date"

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def list(self, request, *args, **kwargs):
        queryset = Recipe.objects.all()

        tag_slugs = self.request.query_params.getlist("tags")
        if tag_slugs:
            queryset = queryset.filter(tags__slug__in=tag_slugs).distinct()

        is_favorited = self.request.query_params.get("is_favorited")
        if is_favorited == "true" and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)

        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        if (
            is_in_shopping_cart == "true"
            and self.request.user.is_authenticated
        ):
            queryset = queryset.filter(shopping_card__user=self.request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            self.filter_queryset(queryset), many=True
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["author"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        tags = request.data["tags"]
        if tags:
            for tag_id in tags:
                tag = Tag.objects.get(pk=tag_id)
                TagRecipe.objects.create(tag=tag, recipe=instance)

        ingredient_recipes = request.data["ingredients"]
        for ingredient in ingredient_recipes:
            data = {
                "ingredient": ingredient["id"],
                "amount": ingredient["amount"],
                "recipe": instance.pk,
            }
            serializer = IngredientRecipeCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        serializer = RecipeReadSerializer(
            instance, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=request.data["id"])
        ingredients = request.data.pop("ingredients")
        tags = request.data.pop("tags")
        IngredientRecipe.objects.filter(recipe=recipe).delete()
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item.get("id"))
            amount = item.get("amount")
            recipe_ingredient = IngredientRecipe.objects.create(
                ingredient=ingredient, recipe=recipe, amount=amount
            )
            recipe_ingredient.save()
        recipe.cooking_time = request.data.pop("cooking_time")
        recipe.name = request.data.pop("name")
        recipe.text = request.data.pop("text")
        if request.data.get("image") is not None:
            recipe.image = request.data.pop("image")
        recipe.save()
        recipe.tags.set(tags)
        serializer = RecipeReadSerializer(recipe, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        following = get_object_or_404(get_user_model(), pk=kwargs.get("id"))
        serializer = SubscribeRequestSerializer(
            context={"request": request}, data={"following": following.pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        serializer = SubscribeResponseSerializer(
            following, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        subscribe = get_object_or_404(
            Subscribe, user=request.user, following=kwargs.get("id")
        )

        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsView(ReadOnlyModelViewSet):
    serializer_class = SubscribeResponseSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_user_model().objects.filter(
            following__in=self.request.user.follower.all()
        )


class FavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get("id"))
        serializer = FavoriteRequestSerializer(
            context={"request": request}, data={"recipe": recipe.pk}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        serializer = FavoriteResponseSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe=kwargs.get("id")
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs.get("id"))
        serializer = ShoppingCartRequestSerializer(
            context={"request": request}, data={"recipe": recipe.pk}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        serializer = ShoppingCartResponseSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        shopping_cart = get_object_or_404(
            ShoppingCart, user=request.user, recipe=kwargs.get("id")
        )

        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadView(APIView):
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        shopping_carts = ShoppingCart.objects.filter(
            user=self.request.user
        ).all()
        recipes = []
        for cart in shopping_carts:
            recipes.append(cart.recipe)

        ingredient_recipes = []
        for recipe in recipes:
            ingredient_recipes_internal = recipe.ingredient_recipe.all()
            for ingredient_recipe_internal in ingredient_recipes_internal:
                ingredient_recipes.append(ingredient_recipe_internal)

        ingredients_dict = {}
        for ingredient_recipe in ingredient_recipes:
            ingredients_dict[ingredient_recipe.ingredient] = 0

        for ingredient_recipe in ingredient_recipes:
            ingredients_dict[
                ingredient_recipe.ingredient
            ] += ingredient_recipe.amount

        wishlist = []
        for ingredient, amount in ingredients_dict.items():
            wishlist.append(
                f"{ingredient.name} - {amount} {ingredient.measurement_unit}\n"
            )
        wishlist.append("\n")
        wishlist.append("Foodgram, 07/2021")
        response = HttpResponse(wishlist, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="wishlist.txt"'
        return response
