from celery import shared_task
from backend.models import Dish, User, DiaryRecord, DailyGoals
from django.db.models import Count
from django.utils.timezone import now
from datetime import timedelta
from django.core.mail import send_mail
import os
from django.utils import timezone
from django.db.models import Sum  
from .utils import recalculate_nutrition_for_today



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






@shared_task

def update_goals():
    user = User.objects.get(id=2)

    # Get yesterday's date range
    yesterday = timezone.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

    # 1. Get yesterday’s diary records
    diary_records = DiaryRecord.objects.filter(
        user=user,
        date__range=[yesterday_start, yesterday_end]
    )

    # 2. Aggregate consumed macros
    totals = diary_records.aggregate(
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbohydrates'),
        total_fats=Sum('fat'),
        total_sugar=Sum('sugar'),
        total_fiber=Sum('fiber'),
        total_caffeine=Sum('caffein'),
    )

    # Ensure no nulls
    consumed = {
        'calories': totals['total_calories'] or 0,
        'protein': totals['total_protein'] or 0,
        'carbohydrates': totals['total_carbs'] or 0,
        'fats': totals['total_fats'] or 0,
        'sugars': totals['total_sugar'] or 0,
        'fiber': totals['total_fiber'] or 0,
        'caffein': totals['total_caffeine'] or 0,
    }

        # 3. Update DailyGoals entry for that date
    daily_goals, _ = DailyGoals.objects.get_or_create(user=user, date=yesterday.date())
    daily_goals.calories = consumed['calories']
    daily_goals.protein = consumed['protein']
    daily_goals.carbohydrates = consumed['carbohydrates']
    daily_goals.fats = consumed['fats']
    daily_goals.sugars = consumed['sugars']
    daily_goals.fiber = consumed['fiber']
    daily_goals.caffein = consumed['caffein']
    daily_goals.save()

    # 4. Send email with summary
    send_mail(
        subject="Your Nutrition Summary from Yesterday",
        message=(
            f"Hi {user.name},\n\n"
            f"Here's a summary of your nutrition intake for {yesterday.date()}:\n\n"
            f"🔹 Calories: {consumed['calories']} kcal / Goal: {user.calories_d} kcal\n"
            f"🔹 Protein: {consumed['protein']} g / Goal: {user.protein_d} g\n"
            f"🔹 Carbohydrates: {consumed['carbohydrates']} g / Goal: {user.carbohydrate_d} g\n"
            f"🔹 Fats: {consumed['fats']} g / Goal: {user.fat_d} g\n"
            f"🔹 Sugars: {consumed['sugars']} g / Goal: {user.sugars_d} g\n"
            f"🔹 Fiber: {consumed['fiber']} g / Goal: {user.fiber_d} g\n"
            f"🔹 Caffeine: {consumed['caffein']} mg / Goal: {user.caffein_d} mg\n\n"
            f"Keep up the good work! 🥦💪"
        ),
        from_email=os.getenv('EMAIL_NAME'),
        recipient_list=[user.email],
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