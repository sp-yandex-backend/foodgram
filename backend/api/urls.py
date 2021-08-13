from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (FavoriteView, IngredientView, RecipeView,
                    ShoppingCartDownloadView, ShoppingCartView, SubscribeView,
                    SubscriptionsView, TagView)

main_router = SimpleRouter()
main_router.register("tags", TagView)
main_router.register("ingredients", IngredientView)
main_router.register("recipes", RecipeView)

urlpatterns = [
    path(
        "users/subscriptions/",
        SubscriptionsView.as_view({"get": "list"}),
        name="subscriptions",
    ),
    path(
        "users/<int:id>/subscribe/", SubscribeView.as_view(), name="subscribe"
    ),
    path(
        "recipes/<int:id>/favorite/", FavoriteView.as_view(), name="favorite"
    ),
    path(
        "recipes/<int:id>/shopping_cart/",
        ShoppingCartView.as_view(),
        name="shopping_cart",
    ),
    path(
        "recipes/download_shopping_cart/",
        ShoppingCartDownloadView.as_view(),
        name="download_shopping_cart",
    ),
    path("", include(main_router.urls)),
]
