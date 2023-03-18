"""
Test for recipe API.
"""
from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def image_upload_url(recipe_id):
    """Create and return an image upload url."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def create_recipe(user, **params):
    """Create and return a recipe."""
    defaults = {
        'title': 'Sample recipe title test',
        'price': Decimal(450.75),
        'description': 'Sample description test.',
        'meal_type': 'Dinner',
        'menu_type': 'Keto',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_user(**params):
    """Create and return new user."""
    return get_user_model().objects.create_user(**params)


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'AUTO Sample recipe',
            'price': Decimal('255.05'),
            'meal_type': 'BREAKFAST',
            'menu_type': 'CLASSIC',
        }

        user = self.user
        user.is_staff = True
        res = self.client.post(RECIPES_URL, payload) # endpoint: /api/recipes/recipe

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test partial update of the recipe."""
        user=self.user
        user.is_staff = True
        original_link = 'https://example.com/test.pdf'
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link
        )

        payload = {'title': 'NEW TITLE'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new ingredients."""
        user = self.user
        user.is_staff = True
        payload = {
            'title': 'AUTO Test Create Recipe',
            'price': Decimal('111.11'),
            'meal_type': 'BREAKFAST',
            'menu_type': 'KETO',
            'ingredients': [
                {'name': 'Ingr One', 'calories': 200, 'weight': 50},
                {'name': 'Ingr Two', 'calories': 1200, 'weight': 150},
                {'name': 'Ingr Three', 'calories': 750, 'weight': 350},
                {'name': 'Ingr Four', 'calories': 505, 'weight': 250},
            ]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 4)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating ingredient when updating recipe."""
        user = self.user
        user.is_staff = True
        recipe = create_recipe(user=self.user)

        payload = {'ingredients': [
                {'name': 'Ingr One', 'calories': 200, 'weight': 50}
            ]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Ingr One')
        self.assertIn(new_ingredient, recipe.ingredients.all())



class ImageUploadTests(TestCase):
    """Tests for img upload API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123',
        )
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
