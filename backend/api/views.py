import base64

from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import SetPasswordSerializer
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from user.models import Subscription, User
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserCreateSerializer, UserListSerializer,
                          UserRetrieveSerializer, UserSerializer)


class UserPagination(PageNumberPagination):
    page_size = 1


class RecipePagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'


class RecipeTagPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        tags = self.request.query_params.getlist('tags')
        if tags:
            self.pagination_class = RecipeTagPagination
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )

        if is_in_shopping_cart == '1' and user.is_authenticated:
            queryset = queryset.filter(in_shopping_cart__user=user)
        elif is_in_shopping_cart == '0' and user.is_authenticated:
            queryset = queryset.exclude(in_shopping_cart__user=user)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited == '1' and user.is_authenticated:
            queryset = queryset.filter(favorited_by=user)
        elif is_favorited == '0' and user.is_authenticated:
            queryset = queryset.exclude(favorited_by=user)

        return queryset

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.author != request.user:
            return Response(
                {'detail': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )

        image_data = request.data.get('image', None)
        if image_data and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(
                base64.b64decode(imgstr),
                name=f'temp.{ext}'
            )
            request.data['image'] = image_data

        serializer = self.get_serializer(
            instance, data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):

        image_data = request.data.get('image', None)
        if not image_data:
            return Response(
                {'detail': 'Поле с изображением обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if image_data and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(
                base64.b64decode(imgstr),
                name=f'temp.{ext}'
            )
            request.data['image'] = image_data

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(recipe.get_absolute_url())
        return Response(
            {'short-link': short_link},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {'detail': 'Этот рецепт уже добавлен в корзину'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=user, recipe=recipe)

            response_data = {
                'id': recipe.id,
                'name': recipe.name,
                'image': request.build_absolute_uri(
                    recipe.image.url) if recipe.image else None,
                'cooking_time': recipe.cooking_time
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            cart_item = user.shopping_cart.filter(recipe=recipe).first()
            if not cart_item:
                return Response(
                    {'detail': 'Этот рецепт не добавлен в корзину.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):

        user = request.user
        shopping_cart = user.shopping_cart.all()

        if not shopping_cart.exists():
            return Response(
                {'detail': 'Корзина пуста.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list = []
        for item in shopping_cart:
            ingredients = item.recipe.ingredients.all()
            for ingredient in ingredients:
                shopping_list.append(
                    f"{ingredient.name} - {ingredient.amount} "
                    f"{ingredient.unit}"
                )

        response = HttpResponse(content_type='text/plain')
        response[
            'Content-Disposition'
        ] = 'attachment; filename="shopping_list.txt"'

        response.write("Список покупок:\n\n")
        for item in shopping_list:
            response.write(f"{item}\n")

        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if request.method == 'POST':
            if recipe in user.favorites.all():
                return Response(
                    {'detail': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorite.objects.create(user=user, recipe=recipe)

            recipe_data = {
                'id': recipe.id,
                'name': recipe.name,
                'image': request.build_absolute_uri(recipe.image.url),
                'cooking_time': recipe.cooking_time
            }

            return Response(recipe_data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not user.favorites.filter(id=recipe.id).exists():
                return Response(
                    {'detail': 'Рецепт не добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        recipe = self.get_object()

        if recipe.author != request.user:
            return Response(
                {'detail': 'У вас нет прав на удаление этого рецепта'},
                status=status.HTTP_403_FORBIDDEN
            )

        recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserRetrieveSerializer
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_serializer = UserCreateSerializer(serializer.instance)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        serializer = UserRetrieveSerializer(
            user,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user

        if request.method == 'PUT':
            avatar_data = request.data.get('avatar', None)
            if avatar_data:
                format, imgstr = avatar_data.split(';base64,')
                ext = format.split('/')[-1]
                avatar = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'{user.username}_avatar.{ext}'
                )
                user.avatar = avatar
                user.save()

                return Response(
                    {'avatar': request.build_absolute_uri(user.avatar.url)},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'detail': 'No avatar provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.save()
                return Response(
                    {'avatar': None},
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response(
                {'detail': 'No avatar to delete.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    from rest_framework.exceptions import PermissionDenied

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'detail': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST)

            if user.follower.filter(author=author).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(user=user, author=author)

            recipes_limit = request.query_params.get('recipes_limit', None)
            context = {'request': request}
            if recipes_limit:
                context['recipes_limit'] = int(recipes_limit)

            serializer = SubscriptionSerializer(author, context=context)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = user.follower.filter(author=author)
            if not subscription.exists():
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        follows = Subscription.objects.filter(
            user=request.user
        ).select_related('author')
        authors = [follow.author for follow in follows]
        pages = self.paginate_queryset(authors)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
