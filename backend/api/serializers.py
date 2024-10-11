from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite
from user.models import User, Subscription


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'



class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')  # Связываем с моделью Ingredient
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')




class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'password',
        )
        read_only_fields = ('id',)

    def create(self, validated_data: dict) -> User:
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
        )

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
        )


class UserRetrieveSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):

        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return Subscription.objects.filter(
                user=request_user,
                author=obj
            ).exists()
        return False




class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')



class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        # Здесь obj — это объект модели User (автор), а не Subscription
        recipes = Recipe.objects.filter(author=obj)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(user=user, author=obj).exists()





class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True, source='recipeingredient_set')
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = serializers.ImageField(required=False)
    author = UserRetrieveSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(recipe=obj, user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        # Проверка, добавлен ли рецепт в список покупок для текущего пользователя
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False

    def update(self, instance, validated_data):
        # Обновление основных полей рецепта
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)

        # Обработка изображения
        image_data = validated_data.get('image', None)
        if image_data:
            instance.image = image_data

        # Сохранение обновленного экземпляра Recipe
        instance.save()

        # Обновление ингредиентов
        ingredients_data = validated_data.get('recipeingredient_set', [])
        if ingredients_data:
            instance.recipeingredient_set.all().delete()  # Удаляем существующие ингредиенты
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data.get(
                    'id')  # Используем .get() для безопасного получения
                amount = ingredient_data.get('amount')
                if ingredient_id is not None and amount is not None:
                    RecipeIngredient.objects.create(
                        recipe=instance,
                        ingredient_id=ingredient_id,
                        amount=amount
                    )

        # Обновление тегов
        tags_data = validated_data.get('tags', [])
        if tags_data:  # Если есть теги для обновления
            instance.tags.clear()  # Очистка существующих тегов
            for tag_id in tags_data:  # Используем только идентификаторы
                if isinstance(tag_id, int):  # Убедимся, что это число
                    instance.tags.add(tag_id)  # Добавляем тег к рецепту

        return instance


    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set', [])
        tags_data = validated_data.pop('tags', [])

        if not ingredients_data:
            raise serializers.ValidationError(
                {"ingredients": "Список ингредиентов не должен быть пустым."})

        # Создаем рецепт
        recipe = Recipe.objects.create(**validated_data)

        # Устанавливаем теги
        recipe.tags.set(tags_data)


        # Создаем ингредиенты
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']

            if amount <= 0:
                raise serializers.ValidationError(
                    {
                        "ingredients": "Количество ингредиента должно быть больше нуля."}
                )

            # Создаем объект RecipeIngredient
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url if instance.image else None
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        return representation


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe  # Убедитесь, что это правильная модель
        fields = ('id', 'name', 'image', 'cooking_time')
