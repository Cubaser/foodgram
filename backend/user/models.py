from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

class User(AbstractUser):

    # username = models.CharField(
    #     verbose_name='Уникальный юзернейм',
    #     max_length=150,
    #     unique=True,
    #     validators=(UnicodeUsernameValidator,)
    # )
    #
    # first_name = models.CharField(
    #     verbose_name='Имя',
    #     max_length=150,
    # )

    email = models.EmailField(unique=True, verbose_name='Почта')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    avatar = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
