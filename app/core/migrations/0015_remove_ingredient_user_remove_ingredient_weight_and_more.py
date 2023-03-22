# Generated by Django 4.1.5 on 2023-03-21 19:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_recipe_image_alter_user_allergy_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='user',
        ),
        migrations.RemoveField(
            model_name='ingredient',
            name='weight',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='price',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='user',
        ),
        migrations.AddField(
            model_name='ingredient',
            name='price',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='users_disliked',
            field=models.ManyToManyField(blank=True, related_name='disliked_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='users_liked',
            field=models.ManyToManyField(blank=True, related_name='liked_recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='RecipeComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('weight', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_in_recipes', to='core.ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='core.recipe')),
            ],
        ),
    ]
