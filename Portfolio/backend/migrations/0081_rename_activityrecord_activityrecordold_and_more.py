# Generated by Django 5.1.3 on 2025-06-12 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0080_activityrecorduuid_dailygoalsuuid'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ActivityRecord',
            new_name='ActivityRecordOLD',
        ),
        migrations.RenameModel(
            old_name='DailyGoals',
            new_name='DailyGoalsOLD',
        ),
    ]
