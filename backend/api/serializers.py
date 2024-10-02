from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient
from user.models import User, Subscription

class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

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
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(
            user=user,
            author=obj
        ).exists()
