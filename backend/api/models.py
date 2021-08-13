from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=100, verbose_name="name")
    measurement_unit = models.CharField(
        max_length=10, verbose_name="measurement_unit"
    )

    class Meta:
        verbose_name = "ingredient"
        verbose_name_plural = "ingredients"


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="name")
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"


class Recipe(models.Model):
    author = models.ForeignKey(
        User, related_name="recipes", on_delete=models.SET_NULL, null=True
    )
    name = models.CharField(max_length=100, verbose_name="name")
    image = models.ImageField(verbose_name="image", upload_to="recipes")
    text = models.TextField(verbose_name="text")
    ingredients = models.ManyToManyField(
        Ingredient, through="IngredientRecipe", verbose_name="ingredients"
    )
    tags = models.ManyToManyField(
        Tag, through="TagRecipe", verbose_name="tags"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="cooking_time", validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="pub_date")

    class Meta:
        verbose_name = "recipe"
        verbose_name_plural = "recipes"

    def count_favorites(self):
        return self.favorite.count()


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
        verbose_name="ingredient",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredient_recipe",
        verbose_name="recipe",
    )
    amount = models.PositiveIntegerField(
        verbose_name="amount", validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = "ingredient_recipe"
        verbose_name_plural = "ingredient_recipes"

    def __str__(self):
        return f"{self.ingredient} {self.recipe}"


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="tag", verbose_name="tag"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="recipe"
    )

    class Meta:
        verbose_name = "tag_recipe"
        verbose_name_plural = "tag_recipes"

    def __str__(self):
        return f"{self.tag} {self.recipe}"


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        null=False,
        verbose_name="user",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        null=False,
        verbose_name="following",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "following"], name="unique_follow"
            ),
        ]
        verbose_name = "subscribe"
        verbose_name_plural = "subscribes"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite",
        null=False,
        verbose_name="user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorite",
        null=False,
        verbose_name="recipe",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite"
            ),
        ]
        verbose_name = "favorite"
        verbose_name_plural = "favorites"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_card",
        null=False,
        verbose_name="user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_card",
        null=False,
        verbose_name="recipe",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_card"
            ),
        ]
        verbose_name = "shopping_cart"
        verbose_name_plural = "shopping_carts"
