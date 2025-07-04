# Generated by Django 5.1.3 on 2025-06-17 07:59

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0084_rename_carbohydrate_dailygoals_carbs_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='caffein_d',
            new_name='caffeine_d',
        ),
        migrations.RenameField(
            model_name='user',
            old_name='carbohydrate_d',
            new_name='carbs_d',
        ),
        migrations.AlterField(
            model_name='dailygoals',
            name='id',
            field=models.UUIDField(default=uuid.UUID('1caf47fb-4c69-4f2b-84a4-fce307222091'), primary_key=True, serialize=False),
        ),
    ]
