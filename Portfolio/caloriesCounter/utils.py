WEIGHT_MODIFIER = {
    "none": 1.0,
    "1-5": 1.05,
    "5-10": 1.1,
    "10-15": 1.15,
    "15+": 1.2,
}


def calculate_calories_from_met(met, weight_kg, duration_minutes, weight_group='none'):
    """General MET-based calculation."""
    adjusted_met = met * WEIGHT_MODIFIER.get(weight_group, 1.0)
    print(adjusted_met, weight_kg, duration_minutes)
    print(round(0.0175 * adjusted_met * weight_kg * duration_minutes))
    return round(0.0175 * adjusted_met * weight_kg * duration_minutes)


def estimate_duration_from_reps(reps, pace="medium"):
    pace_seconds = {"slow": 4, "medium": 2, "fast": 1.2}
    seconds_per_rep = pace_seconds.get(pace, 2)
    return (reps * seconds_per_rep) / 60


def calculate_custom_workout_calories(exercises, weight_kg, default_pace="medium", verbose=False):
    total_calories = 0
    total_time = 0

    for e in exercises:
        reps_total = e.reps * e.sets
        time_minutes = e.time_minutes or estimate_duration_from_reps(reps_total, default_pace)

        calories = calculate_calories_from_met(
            e.exercise.met, weight_kg, time_minutes, e.weight_group
        )

        if verbose:
            print(f"Exercise: {e.exercise.name}, Time: {time_minutes:.2f} min, Calories: {calories}")

        total_calories += calories
        total_time += time_minutes

    return round(total_calories), round(total_time, 2)


def calculate_tabata_calories(exercises, weight_kg, rounds=8, work_sec=20, rest_sec=10, include_rest=False):
    if not exercises:
        return 0

    total_minutes = ((work_sec + rest_sec) * rounds) / 60 if include_rest else (work_sec * rounds) / 60
    time_per_exercise = total_minutes / len(exercises)

    total_calories = 0

    for ex in exercises:
        met = ex.met
        calories = calculate_calories_from_met(met, weight_kg, time_per_exercise)
        total_calories += calories

    return round(total_calories)
 
def calculate_tabata_duration(tabata_data):
    num_exercises = len(tabata_data.get('exercises', []))
    work = tabata_data['work_seconds']
    rest = tabata_data['rest_seconds']
    total_duration = num_exercises * (work + rest) - rest  # No rest after last round
    return total_duration



def calculate_steps_calories(steps, weight_kg, stride_length_m=0.75, pace="moderate"):
    """
    Estimate calories burned from walking steps based on pace category: 'slow', 'moderate', or 'fast'.
    """
    # Approximate MET values based on walking pace
    pace_to_met = {
        "slow": 2.5,       # ~2.5 km/h
        "moderate": 3.5,   # ~4.7 km/h
        "fast": 4.5        # ~5.6 km/h
    }

    met = pace_to_met.get(pace.lower(), 3.5)  # default to moderate if not found

    # Estimate distance in meters
    distance_m = steps * stride_length_m

    # Estimate walking speed in m/min for time estimation (rough)
    pace_to_speed_kmh = {
        "slow": 2.5,
        "moderate": 4.7,
        "fast": 5.6
    }

    speed_kmh = pace_to_speed_kmh.get(pace.lower(), 4.7)
    speed_m_per_min = (speed_kmh * 1000) / 60

    # Calculate time in minutes
    time_minutes = distance_m / speed_m_per_min

    return calculate_calories_from_met(met, weight_kg, time_minutes)




def get_met_for_speed(activity, speed_kmh):
    if activity == 'walk_time':
        if speed_kmh < 5:
            return 3.5  # Slow walk
        elif speed_kmh < 6:
            return 4.0  # Moderate walk
        else:
            return 4.5  # Fast walk
    elif activity == 'run':
        if speed_kmh < 8:
            return 9.8  # Slow run
        elif speed_kmh < 12:
            return 10.1  # Moderate run
        else:
            return 12.0  # Fast run
    elif activity == 'interval_run':
        return 10.5  # Interval run (fixed value, for now)
    else:
        return 1  # Default for unknown activities




def calculate_run_walk_calories(met, weight_kg, time_minutes, distance_km, activity_type):
    # Calculate the average speed in km/h
    speed_kmh = distance_km / (time_minutes / 60)  # speed in km/h
    print(speed_kmh, 'speed')
    adjusted_met = get_met_for_speed(activity_type, speed_kmh)
    # Calculate calories burned
    calories_burned = round(0.0175 * adjusted_met * weight_kg * time_minutes)
    
    return calories_burned
