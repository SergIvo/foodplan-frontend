"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_superuser',
                    'is_subscribed',
                    'subscription_until',
                    'allergy_type',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_superuser',
            )
        }),
    )


class ComponentsInline(admin.TabularInline):
    model = models.RecipeComponent
    raw_id_fields = ('ingredient',)
    fields = ('weight', 'ingredient')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'meal_type', 'menu_type', 'allergy_type')
    list_filter = ('meal_type', 'menu_type', 'allergy_type')
    raw_id_fields = ('users_liked', 'users_disliked')
    
    def show_image(self, obj):
        return format_html(
            '<img style="max-height:200px" src="{url}"/>',
            url=obj.image.url
        )

    show_image.short_description = 'Preview'
    readonly_fields = ('show_image',)
    
    inlines = (ComponentsInline,)


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Ingredient)
