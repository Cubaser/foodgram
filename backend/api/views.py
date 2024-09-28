from rest_framework import viewsets
from recipes.models import Recipe, Tag, Ingredient
from .serializers import (RecipeSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          UserSerializer,
                          )
from user.models import User, Subscription
from rest_framework.permissions import IsAuthenticated
from .serializers import SubscriptionSerializer
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 1

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_serializer_context(self):
        return {'request': self.request}



class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
