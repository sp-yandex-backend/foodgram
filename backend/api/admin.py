from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscribe, Tag, TagRecipe)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = [
        "name",
    ]


class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "author", "count_favorites")
    list_filter = ["name", "author", "tags"]


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe)
admin.site.register(Tag)
admin.site.register(TagRecipe)
admin.site.register(Subscribe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
