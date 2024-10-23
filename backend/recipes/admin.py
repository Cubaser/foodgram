from django.contrib.admin import ModelAdmin, register, TabularInline

from .models import Ingredient, Recipe, Tag, RecipeIngredient


class RecipeIngredientInline(TabularInline):
    model = RecipeIngredient
    extra = 1


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'author',
        'name',
        'cooking_time',
        'get_ingredients',
        'get_tags',
    )
    list_filter = ('author', 'tags', 'cooking_time')
    search_fields = ('name', 'author__username', 'ingredients__name')
    inlines = (RecipeIngredientInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('ingredients', 'tags', 'author')
        return queryset

    def get_ingredients(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    get_ingredients.short_description = 'Ингредиенты'

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Теги'
