# myproject/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Portfolio.settings")
celery_app = Celery("Portfolio")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
celery_app.conf.broker_url = 'redis://localhost:6379/0'


celery_app.conf.beat_schedule = {
    "update-popular-dishes-weekly": {
        "task": "caloriesCounter.tasks.update_popular_dishes",
        "schedule": crontab(hour=8, minute=40, day_of_week=1),  
    },
    "update-balance-daily": {
        "task": "caloriesCounter.tasks.update_calories_balance",
        "schedule": crontab(hour=1, minute=30)
    },
    "update-nutrition-goals-daily": {
        "task": "caloriesCounter.tasks.update_goals",
        "schedule": crontab(hour=1, minute=20)
    },
    "swipe-deleted-instances": {
        "task": "caloriesCounter.tasks.swipe_deleted_instances",
        "schedule": crontab(day_of_week=1)
    }

}
