# Generated by Django 5.1.3 on 2025-05-27 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0040_activityrecord_done'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityrecord',
            name='timestamp',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
