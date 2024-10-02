from itertools import permutations

from rest_framework import viewsets
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
from rest_framework.permissions import IsAuthenticated
from .serializers import SubscriptionSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, response
from rest_framework.decorators import action
import base64
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer


class UserPagination(PageNumberPagination):
    page_size = 1

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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
