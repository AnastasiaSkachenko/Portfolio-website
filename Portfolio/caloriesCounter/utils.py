from django.utils import timezone
from django.db.models import Sum



MET_VALUES = {
    'walk_time': 3.5,
    'walk_steps': 3.0,
    'run': 9.8,
    'interval_run': 10.0,
    'workout': 6.0,
    'tabata': 8.0,
    'custom': 5.0,
    'volleyball': 4.0,
    'stretching': 2.5,
    'jumping': 8.0,
    'home_chores': 3,
}

def calculate_calories_from_activity_record(record):
    user = record.user
    activity_type = record.activity_type
    duration_minutes = record.duration_minutes or 0
    steps = record.steps
    distance_km = record.distance_km
    intensity = record.intensity or 3

    # Use user's weight if not set in activity
    weight_kg = record.weight_kg or getattr(user, 'weight', 70)

    # Convert duration to hours
    duration_hours = duration_minutes / 60.0

    # Get base MET value based on activity type
    met = MET_VALUES.get(activity_type, 5.0)

    # Intensity adjustment (scale 1–5)
    if 1 <= intensity <= 5:
        met *= (0.8 + 0.1 * intensity)  # Adjust MET value based on intensity level

    # Walking (Steps) special case: 0.04 is an approximation for step-based calorie burning
    if activity_type == 'walk_steps' and steps:
        # Base values
        calories_per_step = 0.035  # base for moderate intensity
        base_weight = 70

        # Normalize intensity (e.g., 1.0 for intensity=1, 1.5 for intensity=5)
        # Adjust the scaling factor to tune the influence of intensity
        intensity_multiplier = 1 + (intensity - 3) * 0.2  # ranges from 0.6 to 1.4

        # Apply intensity and weight scaling
        return round(steps * calories_per_step * intensity_multiplier * (weight_kg / base_weight), 0)

    # Walking (Time) special case: burn calories based on MET value and duration
    if activity_type == 'walk_time' and duration_minutes:
        return round(met * weight_kg * duration_hours, 0)

    # Run and Interval Run: These activities are more intense and require MET adjustment for higher intensity
    if activity_type in ['run', 'interval_run'] and duration_minutes:
        # Interval run tends to have higher calorie burn due to sprints, use a slight boost
        if activity_type == 'interval_run':
            met *= 1.2  # Boost MET value for interval runs
        return round(met * weight_kg * duration_hours, 0)
    
    if activity_type == 'home_chores' and duration_minutes:
        duration_hours = duration_minutes / 60
        print('MET', met)
        return round(met * weight_kg * duration_hours, 0)


    # If duration is missing but distance exists, calculate based on distance and MET value
    if duration_minutes == 0 and distance_km:
        return round(distance_km * weight_kg * met, 0)

    # Default MET-based calorie calculation (for activities without special cases)
    calories = met * weight_kg * duration_hours

    return round(calories, 0)



def calculate_bmr(user):
    # Use Mifflin-St Jeor formula as an example
    if user.gender == 'male':
        return 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
    else:
        return 10 * user.weight + 6.25 * user.height - 5 * user.age - 161



def recalculate_nutrition_for_today(user, activity_records):
    today = timezone.now()

    calories_burned_today = activity_records.aggregate(
        total=Sum('calories_burned')
    )['total'] or 0

    bmr = calculate_bmr(user)  

    user.calories_d += bmr + calories_burned_today
    user.bmr = bmr

    # 3. Recalculate daily calorie need
    total_calories = bmr + calories_burned_today

    # 4. Recalculate macros
    # Example macro split: 40% carbs, 30% protein, 30% fat
    protein_ratio = 0.30
    carbs_ratio = 0.40
    fat_ratio = 0.30

    protein_grams = round((total_calories * protein_ratio) / 4)
    carbs_grams = round((total_calories * carbs_ratio) / 4)
    fat_grams = round((total_calories * fat_ratio) / 9)

    # Optionally add sugar, fiber, caffeine if you have rules/formulas
    sugar_ratio = 0.05
    sugar_grams = round((total_calories * sugar_ratio) / 4)

    # Fiber: fixed target (can be customized per user later)
    fiber_grams = 30

    # Caffeine: fixed safe upper limit
    caffeine_mg = 400


    # 5. Save updated values
    user.calories_d = total_calories
    user.protein_d = protein_grams
    user.carbs_d = carbs_grams
    user.fat_d = fat_grams
    user.sugar_d = sugar_grams
    user.fiber_d = fiber_grams
    user.caffeine_d = caffeine_mg
    

    user.save()

    print(f"Updated nutrition for {today.date()}: {total_calories} kcal, {protein_grams}g P, {carbs_grams}g C, {fat_grams}g F")


