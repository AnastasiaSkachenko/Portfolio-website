# Generated by Django 5.1.3 on 2025-06-12 14:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0076_alter_dish_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaryRecordUUID',
            fields=[
                ('id', models.UUIDField(default=None, primary_key=True, serialize=False)),
                ('name', models.CharField(default='food', max_length=150)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('calories', models.IntegerField(null=True)),
                ('protein', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('carbs', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('fat', models.DecimalField(decimal_places=1, max_digits=10, null=True)),
                ('fiber', models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ('sugars', models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ('caffeine', models.DecimalField(decimal_places=1, default=0, max_digits=10)),
                ('weight', models.IntegerField(default=0)),
                ('portions', models.IntegerField(default=0)),
                ('is_deleted', models.BooleanField(default=False)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('dish', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='diaryDishUUIDOwn', to='backend.dish')),
                ('user', models.ForeignKey(default=2, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='userUUID', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
