# Generated by Django 5.1.3 on 2025-06-04 09:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0050_productuuid'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='ProductOld',
        ),
    ]
