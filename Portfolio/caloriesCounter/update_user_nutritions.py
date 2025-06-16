from django.utils import timezone
from backend.models import ActivityRecord, DailyGoals
from datetime import timedelta
from django.db.models import Sum, Q  # import Q for query expressions
from django.db import models
from django.utils.timezone import make_aware, datetime, timedelta
import uuid




#runs when activity created, updated or deleted
def update_daily_goals(user, timestamp, previous_timestamp=None):
    """
    Update or create DailyGoals for user on relevant dates.
    """
    print('----------------------/n/n')


    def safe_value(value, default, min_value=None, max_value=None):
        try:
            val = float(value)
            if min_value is not None and val < min_value:
                return default
            if max_value is not None and val > max_value:
                return default
            return val
        except (TypeError, ValueError):
            return default

    def bmr_calc(weight, height, age, gender):
        if gender == "female":
            return (10 * weight) + (6.25 * height) - (5 * age) - 161
        else:
            return (10 * weight) + (6.25 * height) - (5 * age) + 5

    def update_for_date(date):
        start_of_day = make_aware(datetime.combine(date, datetime.min.time()))
        end_of_day = make_aware(datetime.combine(date + timedelta(days=1), datetime.min.time()))

        # One query with annotation to reduce DB hits
        records_qs = ActivityRecord.objects.filter(user=user, timestamp__gte=start_of_day, timestamp__lt=end_of_day)
        agg = records_qs.aggregate(
            total_burned_goal=Sum('calories_burned'),
            total_burned_done=Sum('calories_burned', filter=models.Q(done=True))
        )
        total_burned_goal = agg['total_burned_goal'] or 0
        total_burned = agg['total_burned_done'] or 0

        age = safe_value(user.age, 30, 5, 120)
        weight = safe_value(user.weight, 70, 20, 500)
        height = safe_value(user.height, 170, 50, 250)
        gender = user.gender if user.gender in ("male", "female") else "male"
        goal = user.goal if user.goal in ("fat_loss", "active_fat_loss", "muscle_gain", "active_muscle_gain", "maintenance") else "maintenance"

        bmr = bmr_calc(weight, height, age, gender)

        total_calories_goal = round(round(bmr * 1.05) + total_burned_goal) if total_burned_goal >= 1 else round(bmr * 1.15)
        total_calories = round(bmr + total_burned) if total_burned >= 1 else round(bmr * 1.15)

        goal_multipliers = {
            "fat_loss": 0.85, "active_fat_loss": 0.75,
            "muscle_gain": 1.15, "active_muscle_gain": 1.25,
            "maintenance": 1.0
        }
        total_calories = round(total_calories * goal_multipliers.get(goal, 1.0))

        protein_targets = {
            "fat_loss": 2.2, "active_fat_loss": 2.4,
            "muscle_gain": 2.4, "active_muscle_gain": 2.6,
            "maintenance": 1.6
        }
        protein_per_kg = protein_targets.get(goal, 1.6)
        protein_goal = round(weight * protein_per_kg)
        protein_calories = protein_goal * 4

        fat_ratios = {
            "fat_loss": 0.25, "active_fat_loss": 0.22,
            "muscle_gain": 0.22, "active_muscle_gain": 0.22,
            "maintenance": 0.25
        }
        fat_ratio = fat_ratios.get(goal, 0.25)
        fat_goal = round((total_calories * fat_ratio) / 9)
        fat_calories = fat_goal * 9

        remaining_calories = max(total_calories - (protein_calories + fat_calories), 0)
        carbohydrate_goal = round(remaining_calories / 4)

        sugar_goal = round((total_calories * 0.10) / 4)
        fiber_goal = round((total_calories / 1000) * 14)
        caffeine_goal = safe_value(getattr(user, 'caffeine_d', 400), 400, 0, 1000)

        print('')

        if isinstance(date, datetime):
            date = date.date()  # convert to date only
    

        print('previous timestamp', previous_timestamp)
        print('date ', date)
        daily_goals, created = DailyGoals.objects.update_or_create(
            user=user,
            date=date,
            defaults={
                'calories_burned': total_burned,
                'calories_burned_goal': total_burned_goal,
                'calories_intake_goal': total_calories_goal,
                'protein_goal': protein_goal,
                'carbohydrate_goal': carbohydrate_goal,
                'fat_goal': fat_goal,
                'sugars_goal': sugar_goal,
                'fiber_goal': fiber_goal,
                'caffeine_goal': caffeine_goal,
            }
        )
        print(daily_goals.calories_intake_goal, 'daily goal calories intake goal')
        print(daily_goals.date, 'daily goal date')

        if created: 
            print('daily goals is created')
        return daily_goals

    if user is None or timestamp is None:
        raise ValueError("User and timestamp are required")

    new_date = timestamp.date()
    old_date = previous_timestamp.date() if previous_timestamp else None

    update_for_date(new_date)


    print(old_date, 'old date')
    print(new_date, 'new date')

    if old_date and old_date != new_date:
        update_for_date(old_date)



#runs when user info is updated
def update_user_nutrition(user):
    """
    Update user nutrition profile using pre-calculated activity calories and user data.
    Calculates: calories, protein, fats, carbs, sugars, fiber, caffeine.
    """

    age = user.age
    weight = user.weight  # in kg
    height = user.height  # in cm
    activity_level = user.activity_level
    gender = user.gender
    goal = user.goal
    calculate_from_activity = user.calculate_nutritions_from_activity_level

    # 1. BMR Calculation (Mifflin-St Jeor Equation)
    if gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    total_calories = bmr

    # 2. Add calories based on activity level or pre-calculated activity
    if calculate_from_activity:
        activity_multipliers = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        multiplier = activity_multipliers.get(activity_level, 1.2)
        total_calories = bmr * multiplier
    else:
        # Calculate average calories burned from workouts in the past 7 days
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        recent_records = ActivityRecord.objects.filter(user=user, timestamp__gte=seven_days_ago)

        total_burned = recent_records.aggregate(Sum('calories_burned'))['calories_burned__sum'] or 0

        average_daily_burn = total_burned / 7 if total_burned else 0
        total_calories = round(bmr + average_daily_burn)



    total_calories = round(total_calories)

    # 3. Adjust for Goal
    goal_multipliers = {
        "fat_loss": 0.85, "active_fat_loss": 0.75,
        "muscle_gain": 1.15, "active_muscle_gain": 1.25,
        "maintenance": 1.0
    }
    total_calories = round(total_calories * goal_multipliers.get(goal, 1.0))

    # 4. Protein
    protein_targets = {
        "fat_loss": 2.2, "active_fat_loss": 2.4,
        "muscle_gain": 2.4, "active_muscle_gain": 2.6,
        "maintenance": 1.7
    }
    protein_per_kg = protein_targets.get(goal, 1.7)
    protein_d = round(weight * protein_per_kg)
    protein_calories = protein_d * 4

    # 5. Fat
    fat_ratios = {
        "fat_loss": 0.25, "active_fat_loss": 0.22,
        "muscle_gain": 0.22, "active_muscle_gain": 0.22,
        "maintenance": 0.25
    }
    fat_ratio = fat_ratios.get(goal, 0.25)
    fat_d = round((total_calories * fat_ratio) / 9)
    fat_calories = fat_d * 9

    # 6. Carbohydrates
    remaining_calories = total_calories - (protein_calories + fat_calories)
    carbohydrate_d = round(remaining_calories / 4)

    # 7. Sugars (10% of calories)
    sugar_d = round((total_calories * 0.10) / 4)

    # 8. Fiber (14g per 1000 kcal)
    fiber_d = round((total_calories / 1000) * 14)

    # 9. Caffeine (default to 0 or take from user if defined)
    caffeine_mg = getattr(user, 'caffein_d', 400)

    # Save values to user
    user.calories_d = total_calories
    user.protein_d = protein_d
    user.carbohydrate_d = carbohydrate_d
    user.fat_d = fat_d
    user.sugars_d = sugar_d
    user.fiber_d = fiber_d
    user.caffein_d = caffeine_mg
    user.save()

    return user
