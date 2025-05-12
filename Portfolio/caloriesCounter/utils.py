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
        # More accurate step-based calorie burn based on MET value
        met_walk = MET_VALUES.get('walk_steps', 3.0)
        return round(steps * 0.04 * met_walk, 0)

    # Walking (Time) special case: burn calories based on MET value and duration
    if activity_type == 'walk_time' and duration_minutes:
        return round(met * weight_kg * duration_hours, 0)

    # Run and Interval Run: These activities are more intense and require MET adjustment for higher intensity
    if activity_type in ['run', 'interval_run'] and duration_minutes:
        # Interval run tends to have higher calorie burn due to sprints, use a slight boost
        if activity_type == 'interval_run':
            met *= 1.2  # Boost MET value for interval runs
        return round(met * weight_kg * duration_hours, 0)

    # If duration is missing but distance exists, calculate based on distance and MET value
    if duration_minutes == 0 and distance_km:
        return round(distance_km * weight_kg * met, 0)

    # Default MET-based calorie calculation (for activities without special cases)
    calories = met * weight_kg * duration_hours

    return round(calories, 0)
