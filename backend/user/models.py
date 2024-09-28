from django.contrib.auth.models import AbstractUser
#from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.conf import settings

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

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'author')

