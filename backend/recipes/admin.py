from django.contrib.admin import ModelAdmin, register
from .models import Tag, Ingredient, Recipe


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    prepopulated_fields = {'slug': ('name',)}

@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )

@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'author',
        'name',
        'image',
        'text',
        'cooking_time',
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('ingredients', 'tags')
        return queryset