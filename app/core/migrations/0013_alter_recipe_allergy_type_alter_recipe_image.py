# Generated by Django 4.1.5 on 2023-03-17 10:13

import core.models
from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='allergy_type',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[('NONE', 'None'), ('FISH', 'Fish'), ('MEAT', 'Meat'), ('GRAIN', 'Grain'), ('HONEY', 'Honey'), ('NUTS', 'Nuts'), ('LACTOSE', 'Lactose')], max_length=125),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.recipe_image_file_path),
        ),
    ]