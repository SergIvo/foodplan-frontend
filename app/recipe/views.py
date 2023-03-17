"""
Views for recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Recipe, Ingredient
from recipe import serializers

from django.shortcuts import HttpResponse


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'allergy_type',
                OpenApiTypes.STR,
                description='Comma separated list of allergies to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredients to filter',
            ),
            OpenApiParameter(
                'meal_type',
                OpenApiTypes.STR,
                description='Comma separated list of meal types to filter',
            ),
            OpenApiParameter(
                'menu_type',
                OpenApiTypes.STR,
                description='Comma separated list of menu types to filter',
            ),
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def _params_to_str(self, qs):
        """Convert a list of strings to strings."""
        return [str(str_id) for str_id in qs.split(', ')]

    def get_queryset(self):
        """Retrieve recipes."""
        allergy_type = self.request.query_params.get('allergy_type')
        ingredients = self.request.query_params.get('ingredients')
        meal_type = self.request.query_params.get('meal_type')
        menu_type = self.request.query_params.get('menu_type')

        queryset = self.queryset
        if allergy_type:
            allergy_ids = self._params_to_str(allergy_type)
            queryset = queryset.filter(allergy_type__in=[allergy_ids])
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        if meal_type:
            meal_type_ids = self._params_to_str(meal_type)
            queryset = queryset.filter(meal_type__in=meal_type_ids)
        if menu_type:
            menu_type_ids = self._params_to_str(menu_type)
            queryset = queryset.filter(menu_type__in=menu_type_ids)

        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        """Return serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        user = self.request.user
        if user.is_staff:
            serializer.save(user=self.request.user)
        else:
            return HttpResponse('Forbidden for not staff users.', status=403)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.order_by('-name').distinct()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
