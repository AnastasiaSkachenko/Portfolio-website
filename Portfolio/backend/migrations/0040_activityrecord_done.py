# Generated by Django 5.1.3 on 2025-05-27 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0039_rename_caffein_dailygoals_caffeine_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityrecord',
            name='done',
            field=models.BooleanField(default=True),
        ),
    ]
