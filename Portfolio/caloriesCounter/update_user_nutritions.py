from django.utils import timezone
from backend.models import ActivityRecord, DailyGoals
from datetime import timedelta
from django.db.models import Sum
from django.utils.timezone import make_aware, datetime, timedelta





#runs when activity created, updated or deleted
def update_daily_goals(user, for_date=None):
    """
    Update or create a DailyGoals record for a user on a specific date.
    Recalculates calorie, protein, carb, fat, sugar, fiber, caffeine goals.
    """

    if for_date is None:
        for_date = timezone.now().date()

    start_of_day = make_aware(datetime.combine(for_date, datetime.min.time()))
    end_of_day = make_aware(datetime.combine(for_date + timedelta(days=1), datetime.min.time()))

    records = ActivityRecord.objects.filter(user=user, timestamp__gte=start_of_day, timestamp__lt=end_of_day)
    print(len(records), 'len records')
        
    total_burned = sum([record.calories_burned for record in records]) or 0

    
    # Step 2: Calculate BMR
    age = user.age
    weight = user.weight
    height = user.height
    gender = user.gender
    goal = user.goal

    if gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    # Step 3: Total calories = BMR + activity
    total_calories = round(bmr * 1.1 + total_burned )

    # Step 4: Adjust for goal
    goal_multipliers = {
        "fat_loss": 0.85, "active_fat_loss": 0.75,
        "muscle_gain": 1.15, "active_muscle_gain": 1.25,
        "maintenance": 1.0
    }
    total_calories = round(total_calories * goal_multipliers.get(goal, 1.0))

    # Step 5: Macronutrient splits
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

    remaining_calories = total_calories - (protein_calories + fat_calories)
    carbohydrate_goal = round(remaining_calories / 4)

    sugar_goal = round((total_calories * 0.10) / 4)
    fiber_goal = round((total_calories / 1000) * 14)
    caffeine_goal = getattr(user, 'caffeine_mg', 0)

    # Step 6: Create or update DailyGoals
    daily_goals, created = DailyGoals.objects.get_or_create(user=user, date=for_date)

    daily_goals.calories_burned = total_burned
    daily_goals.calories_burned_goal = total_burned  # same for now
    daily_goals.calories_intake_goal = total_calories

    daily_goals.protein_goal = protein_goal
    daily_goals.carbohydrate_goal = carbohydrate_goal
    daily_goals.fat_goal = fat_goal
    daily_goals.sugars_goal = sugar_goal
    daily_goals.fiber_goal = fiber_goal
    daily_goals.caffein_goal = caffeine_goal

    daily_goals.save()

    return daily_goals


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
        "maintenance": 1.6
    }
    protein_per_kg = protein_targets.get(goal, 1.6)
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
    caffeine_mg = getattr(user, 'caffein_d', 0)

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
