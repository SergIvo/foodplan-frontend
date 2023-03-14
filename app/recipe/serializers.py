"""
Serializers for recipe API.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'price',
            'meal_type',
            'allergy_type',
            'menu_type',
        ]
        read_only_fields = ['id', 'user']
