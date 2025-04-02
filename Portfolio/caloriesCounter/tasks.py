from celery import shared_task
from backend.models import Dish, User, DiaryRecord
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
import os
from django.utils import timezone
from django.db.models import Sum  



@shared_task
def update_popular_dishes():
    print('Scheduled update for popular dishes')

    POPULARITY_THRESHOLD = 2
    RECORD_THRESHOLD = 5

    # Compute popularity metrics
    twenty_days_ago = now() - timedelta(days=20)

    # Reset previous popular dishes
    Dish.objects.filter(is_popular=True).update(is_popular=False)

    # Get dishes and annotate them with counts
    popular = Dish.objects.filter(
        diaryDish__date__gte=twenty_days_ago,
        product__isnull=True
    ).annotate(
        record_count=Count("diaryDish"), 
        fav_count=Count("favorited_by")
    )

    # Gather all dishes to be updated
    dishes_to_update = []

    for dish in popular:
        if dish.fav_count >= POPULARITY_THRESHOLD or dish.record_count >= RECORD_THRESHOLD:
            dish.is_popular = True
            dishes_to_update.append(dish)

    # Bulk update only the new popular dishes
    if dishes_to_update:
        Dish.objects.bulk_update(dishes_to_update, ["is_popular"])

    # Get the updated popular dishes
    popular_dishes = Dish.objects.filter(is_popular=True)

    # Prepare a list of popular dish names
    dish_names = [dish.name for dish in popular_dishes]
    print(len(dish_names))

    message = f"New popular dishes are: {', '.join(dish_names)}" if dish_names else "No popular dishes currently."

    # Send the email
    send_mail(
        subject="Popularity updates",
        message=message,
        from_email=os.getenv('EMAIL_NAME'),
        recipient_list=["nastaskacenko02@gmail.com"],
        fail_silently=False,
    )

    print("Popularity update completed.")

@shared_task
def update_calories_balance():
    print(' scheduled update calories')

    user = User.objects.get(id=2)

    yesterday = timezone.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    me = None

    records = DiaryRecord.objects.filter(user=user,date__range=[yesterday_start, yesterday_end])
    calories_sum = records.aggregate(Sum('calories'))['calories__sum'] or 0
    difference = user.calories_d  - calories_sum
    print('balance before', user.balance)
    user.balance += difference
    user.save()
    print("Calories sum", calories_sum, "user.calories d", user.calories_d, "difference",difference, 'balance', user.balance)



    
    send_mail(
        subject="updated balance",
        message=f"My calories balance {user.balance}. Difference is {difference}",
        from_email=os.getenv('EMAIL_NAME'),
        recipient_list=["nastaskacenko02@gmail.com"],
        fail_silently=False,
    )



'''
@shared_task
def update_calories_balance():
    print(' scheduled update calories')

    users = User.objects.all()

    yesterday = timezone.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    me = None
    for user in users:

        records = DiaryRecord.objects.filter(user=user,date__range=[yesterday_start, yesterday_end])
        calories_sum = records.aggregate(Sum('calories'))['calories__sum'] or 0
        difference = user.calories_d  - calories_sum
        print("Calories sum", calories_sum, "user.calories d", user.calories_d)
        user.balance += difference
        #user.save()
        if user.id == 2:
            me = user.balance


    
    send_mail(
        subject="updated balance",
        message=f"My calories balance {me}. Difference is {difference}",
        from_email=os.getenv('EMAIL_NAME'),
        recipient_list=["nastaskacenko02@gmail.com"],
        fail_silently=False,
    )

'''