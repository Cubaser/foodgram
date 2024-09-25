from django.db import models
from django.contrib.auth import get_user_model

User= get_user_model()

class Tag(models.Model):
    title = ...
    slug = ...

class Ingredient(models.Model):
    title = ...
    unit = ...


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ForeignKey(

    )
    tags = ...
    cooking_time = ...