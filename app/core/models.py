"""
Database models.
"""
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from multiselectfield import MultiSelectField


def recipe_image_file_path(instance, filename):
    """Generate file path for recipe image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save, and return new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    ALLERGY_TYPE_CHOICES = (
        ("NONE", "None"),
        ("FISH", "Fish"),
        ("MEAT", "Meat"),
        ("GRAIN", "Grain"),
        ("HONEY", "Honey"),
        ("NUTS", "Nuts"),
        ("LACTOSE", "Lactose"),
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_subscribed = models.BooleanField(default=False)
    subscription_until = models.DateTimeField(blank=True, null=True)
    allergy_type = MultiSelectField(
        choices=ALLERGY_TYPE_CHOICES, 
        max_choices=6, 
        max_length=125, 
        blank=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'


class RecipeQuerySet(models.QuerySet):
    def order_by_user_interest(self, user):
        liked = self.filter(users_liked__id__exact=user.id).annotate(user_interest=models.Value(1))
        disliked = self.filter(users_disliked__id__exact=user.id).annotate(user_interest=models.Value(-1))
        neutral = (self.exclude(users_liked__id__exact=user.id)
            .exclude(users_disliked__id__exact=user.id)
            .annotate(user_interest=models.Value(0))
        )
        ordered_recipes = liked.union(disliked, neutral).order_by('-user_interest')
        return ordered_recipes


class Recipe(models.Model):
    """Recipe object."""

    MEAL_TYPE_CHOICES = (
        ("BREAKFAST", "Breakfast"),
        ("LUNCH", "Lunch"),
        ("DINNER", "Dinner"),
        ("DESSERT", "Dessert"),
    )

    ALLERGY_TYPE_CHOICES = (
        ("NONE", "None"),
        ("FISH", "Fish"),
        ("MEAT", "Meat"),
        ("GRAIN", "Grain"),
        ("HONEY", "Honey"),
        ("NUTS", "Nuts"),
        ("LACTOSE", "Lactose"),
    )

    MENU_TYPE_CHOICES = (
        ("CLASSIC", "Classic"),
        ("LOW CARB", "Low Carb"),
        ("VEGETERIAN", "Vegeterian"),
        ("KETO", "Keto"),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meal_type = models.CharField(max_length=9, choices=MEAL_TYPE_CHOICES)
    allergy_type = MultiSelectField(choices=ALLERGY_TYPE_CHOICES, max_choices=6, max_length=125, blank=True)
    menu_type = models.CharField(
        max_length=10,
        choices=MENU_TYPE_CHOICES)
    link = models.CharField(max_length=255, blank=True)
    image = models.ImageField(null=True, blank=True)
    users_liked = models.ManyToManyField(
        User,
        related_name='liked_recipes',
        blank=True)
    users_disliked = models.ManyToManyField(
        User,
        related_name='disliked_recipes',
        blank=True)

    objects = RecipeQuerySet.as_manager()

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ingredient."""

    name = models.CharField(max_length=255)
    calories = models.PositiveSmallIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class RecipeComponentQuerySet(models.QuerySet):
    def with_price(self):
        components_with_price = self.annotate(
            price=models.F('ingredient__price') * models.F('weight') / 1000
            )
        return components_with_price
    
    def with_calories(self):
        components_with_calories = self.annotate(
            calories=models.F('ingredient__calories') * models.F('weight') / 100
            )
        return components_with_calories



class RecipeComponent(models.Model):
    """Ingredient measuerd for recipe."""

    name = models.CharField(max_length=255)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='components'
    )
    weight = models.PositiveSmallIntegerField(blank=True, null=True)

    objects = RecipeComponentQuerySet.as_manager()

    def __str__(self):
        return self.name 
       
