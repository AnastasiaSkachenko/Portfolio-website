# Generated by Django 5.1.3 on 2025-02-28 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0012_dish_weight_of_ready_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dish',
            name='weight_of_ready_product',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
