# Generated by Django 5.1.3 on 2025-01-30 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(default='woman', max_length=10),
        ),
        migrations.AddField(
            model_name='user',
            name='goal',
            field=models.CharField(default='loss', max_length=20),
        ),
    ]
