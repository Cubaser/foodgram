from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RecipeViewSet,
                    TagViewSet,
                    IngredientViewSet,
                    UserViewSet,
                    SubscriptionViewSet
                    )

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', UserViewSet)
router.register(r'subscriptions', SubscriptionViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
