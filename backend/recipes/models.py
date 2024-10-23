from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from foodgram.constants import Constants

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=Constants.TAG_NAME_MAX_LENGTH,
        verbose_name='Название',
        unique=True
    )
    slug = models.SlugField(
        max_length=Constants.TAG_SLUG_MAX_LENGTH,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=Constants.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название',
        unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=Constants.INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    name = models.CharField(
        max_length=Constants.RECIPE_NAME_MAX_LENGTH,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        related_name='recipe'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                Constants.COOKING_TIME_MIN,
                'Слишком низкое значение'
            ),
            MaxValueValidator(
                Constants.COOKING_TIME_MAX,
                'Слишком высокое значение'
            )
        ]
    )
    favorited_by = models.ManyToManyField(
        User,
        through='Favorite',
        related_name='favorites',
        blank=True
    )

    def get_absolute_url(self):
        return reverse('recipes-detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                Constants.AMOUNT_MIN,
                'Слишком низкое значение'
            ),
            MaxValueValidator(
                Constants.AMOUNT_MAX,
                'Слишком высокое значение'
            )
        ]
    )

    class Meta:
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        ordering = ['recipe']

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='in_shopping_cart',
        on_delete=models.CASCADE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        ordering = ['added_at']

    def __str__(self):
        return f'{self.recipe} в корзине {self.user}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ['user', 'recipe']
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['user', 'recipe']

    def __str__(self):
        return f'{self.recipe} в избранном у {self.user}'
