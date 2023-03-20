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
    is_staff = models.BooleanField(default=False)
    is_subscribed = models.BooleanField(default=False)
    subscription_until = models.DateTimeField(blank=True, null=True)
    allergy_type = MultiSelectField(choices=ALLERGY_TYPE_CHOICES, max_choices=6, max_length=125, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'


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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='created_by',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    meal_type = models.CharField(max_length=9, choices=MEAL_TYPE_CHOICES)
    allergy_type = MultiSelectField(choices=ALLERGY_TYPE_CHOICES, max_choices=6, max_length=125, blank=True)
    menu_type = models.CharField(
        max_length=10,
        choices=MENU_TYPE_CHOICES)
    link = models.CharField(max_length=255, blank=True)
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    """Ingredient for recipes."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name='added_by',
    )
    calories = models.PositiveSmallIntegerField(blank=True, null=True)
    weight = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
