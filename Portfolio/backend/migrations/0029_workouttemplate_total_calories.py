# Generated by Django 5.1.3 on 2025-04-23 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0028_workoutexercise_sets'),
    ]

    operations = [
        migrations.AddField(
            model_name='workouttemplate',
            name='total_calories',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
