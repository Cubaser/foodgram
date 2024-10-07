
from rest_framework import viewsets, filters
from recipes.models import Recipe, Tag, Ingredient
from .serializers import (RecipeSerializer,
                          TagSerializer,
                          IngredientSerializer,
                          UserSerializer,
                          UserCreateSerializer,
                          UserListSerializer,
                          UserRetrieveSerializer
                          )
from user.models import User, Subscription
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .serializers import SubscriptionSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, response
from rest_framework.decorators import action
import base64
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer
from django_filters.rest_framework import DjangoFilterBackend


class UserPagination(PageNumberPagination):
    page_size = 1

class RecipePagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'limit'

class RecipeTagPagination(PageNumberPagination):
    page_size_query_param = 'limit'

# class RecipeViewSet(viewsets.ModelViewSet):
#     queryset = Recipe.objects.all()
#     serializer_class = RecipeSerializer
#     pagination_class = RecipePagination
#     filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
#     ordering_fields = '__all__'
#     #ordering = ['id']
#     #permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Фильтрация по автору
#         author_id = self.request.query_params.get('author')
#         if author_id is not None:
#             queryset = queryset.filter(author_id=author_id)
#
#         # Фильтрация по тегам
#         tags = self.request.query_params.getlist('tags')
#         if tags:
#             self.pagination_class = RecipeTagPagination
#             queryset = queryset.filter(tags__slug__in=tags).distinct()
#
#         return queryset
#
#     def update(self, request, *args, **kwargs):
#         # Извлекаем текущее изображение
#         instance = self.get_object()
#
#         # Извлекаем изображение из запроса
#         image_data = request.data.get('image', None)
#
#         # Если изображение передано в формате base64
#         if image_data and image_data.startswith('data:image'):
#             format, imgstr = image_data.split(';base64,')
#             ext = format.split('/')[-1]
#             # Генерируем имя файла и декодируем base64
#             image_data = ContentFile(base64.b64decode(imgstr),
#                                      name=f'temp.{ext}')
#             # Заменяем в запросе значение 'image' декодированным файлом
#             request.data['image'] = image_data
#
#         # Передаем данные в сериализатор
#         serializer = self.get_serializer(instance, data=request.data,
#                                          partial=True)
#         serializer.is_valid(raise_exception=True)
#         self.perform_update(serializer)
#         return response.Response(serializer.data)
#
#
#     def create(self, request, *args, **kwargs):
#         # Извлекаем изображение из запроса
#         image_data = request.data.get('image', None)
#
#         # Если изображение передано в формате base64
#         if image_data and image_data.startswith('data:image'):
#             format, imgstr = image_data.split(';base64,')
#             ext = format.split('/')[-1]
#             # Генерируем имя файла и декодируем base64
#             image_data = ContentFile(base64.b64decode(imgstr),
#                                      name=f'temp.{ext}')
#             # Заменяем в запросе значение 'image' декодированным файлом
#             request.data['image'] = image_data
#
#         # Передаем данные в сериализатор
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#
#         return response.Response(serializer.data, status=status.HTTP_201_CREATED,
#                         headers=headers)
#
#     def perform_create(self, serializer):
#         # Сохраняем объект с сериализованными данными
#         serializer.save(author=self.request.user)
#
#     @action(detail=True, methods=['get'], url_path='get-link')
#     def get_short_link(self, request, pk=None):
#         recipe = self.get_object()  # Получаем объект рецепта по ID
#
#         # Здесь вы можете создать короткую ссылку
#         # Для примера мы просто вернем URL рецепта, вы можете заменить это на свою логику
#         short_link = request.build_absolute_uri(recipe.get_absolute_url())
#
#         return response.Response({'short-link': short_link}, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    ordering_fields = '__all__'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по автору
        author_id = self.request.query_params.get('author')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)

        # Фильтрация по тегам
        tags = self.request.query_params.getlist('tags')
        if tags:
            self.pagination_class = RecipeTagPagination
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        return queryset

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #
    #     # Извлекаем изображение из запроса
    #     image_data = request.data.get('image', None)
    #     if image_data and image_data.startswith('data:image'):
    #         format, imgstr = image_data.split(';base64,')
    #         ext = format.split('/')[-1]
    #         image_data = ContentFile(base64.b64decode(imgstr),
    #                                  name=f'temp.{ext}')
    #         request.data['image'] = image_data
    #
    #     serializer = self.get_serializer(instance, data=request.data,
    #                                      partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return response.Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверка, что текущий пользователь — автор рецепта
        if instance.author != request.user:
            return response.Response({
                                         'detail': 'You do not have permission to perform this action.'},
                                     status=status.HTTP_403_FORBIDDEN)

        # Проверка ингредиентов
        ingredients = request.data.get('ingredients')
        if not ingredients or len(ingredients) < 1:
            return response.Response(
                {'detail': 'At least one ingredient is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на дублирование ингредиентов
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            return response.Response(
                {'detail': 'Ingredients must be unique.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка тегов
        tags = request.data.get('tags')
        if not tags:
            return response.Response(
                {'detail': 'Field "tags" is required and cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на дублирование тегов
        if len(tags) != len(set(tags)):
            return response.Response(
                {'detail': 'Tags must be unique.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Обработка изображения
        image_data = request.data.get('image', None)
        if image_data and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(imgstr),
                                     name=f'temp.{ext}')
            request.data['image'] = image_data

        serializer = self.get_serializer(instance, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return response.Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # Извлекаем ингредиенты из запроса
        ingredients = request.data.get('ingredients', [])
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        # Проверка на дубликаты ингредиентов
        if len(ingredient_ids) != len(set(ingredient_ids)):
            return response.Response(
                {"detail": "Ингредиенты должны быть уникальными."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на наличие тэгов
        tags = request.data.get('tags', [])
        if not tags:
            return response.Response(
                {"detail": "Теги не могут быть пустыми."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на дубликаты тэгов
        if len(tags) != len(set(tags)):
            return response.Response(
                {"detail": "Теги должны быть уникальными."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка на наличие изображения
        image_data = request.data.get('image', None)
        if not image_data:
            return response.Response(
                {"detail": "Поле с изображением обязательно."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Если изображение передано в формате base64
        if image_data and image_data.startswith('data:image'):
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            image_data = ContentFile(base64.b64decode(imgstr),
                                     name=f'temp.{ext}')
            request.data['image'] = image_data

        # Передаем данные в сериализатор
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED,
                                 headers=headers)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = request.build_absolute_uri(recipe.get_absolute_url())
        return response.Response({'short-link': short_link},
                                 status=status.HTTP_200_OK)


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
        elif self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_serializer = UserCreateSerializer(serializer.instance)
        return response.Response(
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
        return response.Response(serializer.data)

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

                return response.Response(
                    {'avatar': request.build_absolute_uri(user.avatar.url)},
                    status=status.HTTP_200_OK
                )
            return response.Response(
                {'detail': 'No avatar provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.save()
                return response.Response(
                    {'avatar': None},
                    status=status.HTTP_204_NO_CONTENT
                )
            return response.Response(
                {'detail': 'No avatar to delete.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = self.request.user
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)



class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)
