from datetime import date, timedelta
from django.db.models import Avg, Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from backend.models import DailyGoals, Dish 
from calendar import monthrange
from rest_framework import  status 
from backend.serializers import DailyGoalSerializer


@api_view(["GET"])
def get_monthly_nutrition_stats(request):
    user = request.user

    try:
        month = int(request.query_params.get("month", date.today().month))
        year = int(request.query_params.get("year", date.today().year))
    except (TypeError, ValueError):
        return Response({"error": "Invalid month or year"}, status=400)

    # Calculate first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # Filter DailyGoals
    goals = DailyGoals.objects.filter(
        user=user,
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date')
    # Sum all actuals and goals
    totals = goals.aggregate(
        total_calories_intake=Sum("calories_intake"),
        total_calories_intake_goal=Sum("calories_intake_goal"),
        total_protein=Sum("protein"),
        total_protein_goal=Sum("protein_goal"),
        total_fat=Sum("fat"),
        total_fat_goal=Sum("fat_goal"),
        total_carbs=Sum("carbs"),
        total_carbs_goal=Sum("carbs_goal"),
        total_fiber=Sum("fiber"),
        total_fiber_goal=Sum("fiber_goal"),
        total_sugars=Sum("sugars"),
        total_sugars_goal=Sum("sugars_goal"),
        total_caffeine=Sum("caffeine"),
        total_caffeine_goal=Sum("caffeine_goal"),
    )

    serializer = DailyGoalSerializer(goals, many=True)
    feedback = generate_feedback(totals)
    suggested_dishes = suggest_dishes(totals)

    return Response({"goals":serializer.data, "feedback":feedback, "suggested_dishes":suggested_dishes}, status=status.HTTP_200_OK)


def generate_feedback(stats):
    feedback = {}

    def analyze(nutrient):
        actual = stats.get(f"total_{nutrient}", 0)
        goal = stats.get(f"total_{nutrient}_goal", 1)  # avoid div by 0
        ratio = actual / goal

        # Calories get a different style of feedback
        if nutrient == "calories_intake":
            if ratio > 1.25:
                feedback[nutrient] = f"You consume significantly more calories than your goal ({int(ratio * 100)}% of target). Try reducing your portion sizes or high-calorie foods."
            elif ratio > 1.1:
                feedback[nutrient] = f"You consume moderately more calories than your goal. Slightly reducing your intake could help."
            elif ratio < 0.75:
                feedback[nutrient] = f"You consume significantly fewer calories than your goal ({int(ratio * 100)}% of target). Make sure you’re eating enough to fuel your body."
            elif ratio < 0.9:
                feedback[nutrient] = f"You consume slightly fewer calories than your goal. Consider eating a bit more."
        else:
            # Other nutrients
            if ratio > 1.25:
                feedback[nutrient] = f"You significantly overconsume {nutrient.capitalize()} (about {int(ratio * 100)}% of your goal). Try reducing foods high in {nutrient}."
            elif ratio > 1.1:
                feedback[nutrient] = f"You moderately overconsume {nutrient.capitalize()}. Consider slightly lowering your intake."
            elif ratio < 0.75:
                feedback[nutrient] = f"You significantly underconsume {nutrient.capitalize()} (only {int(ratio * 100)}% of your goal). Make sure to eat more foods rich in {nutrient}."
            elif ratio < 0.9:
                feedback[nutrient] = f"You slightly underconsume {nutrient.capitalize()}. Try increasing your intake a bit."

    for nutrient in ["calories_intake", "protein", "fat", "carbs", "fiber", "sugars", "caffeine"]:
        analyze(nutrient)

    return feedback

def suggest_dishes(stats):
    suggestions = []

    # Calculate ratios
    def ratio(n): return (stats.get(f"total_{n}", 0)) / (stats.get(f"total_{n}_goal", 1))

    fat_ratio = ratio("fat")
    carb_ratio = ratio("carbs")
    protein_ratio = ratio("protein")
    fiber_ratio = ratio("fiber")
    sugar_ratio = ratio("sugars")
    caffeine_ratio = ratio("caffeine")

    # Examples:
    if fat_ratio > 1.1 and carb_ratio < 0.9:
        dishes = Dish.objects.filter(fat_100__lt=10, carbs_100__gt=20).order_by("-carbs")[:5]
        suggestions.append({
            "message": "You are eating too much fat and not enough carbs. Try these lower-fat, higher-carb dishes:",
            "dishes": [{"name": d.name, "id": d.id, "type": d.type,  "fat": d.fat_100, "carbs": d.carbs_100} for d in dishes]
        })

    if protein_ratio < 0.9:
        dishes = Dish.objects.filter(protein_100__gt=20).order_by("-protein")[:5]
        suggestions.append({
            "message": "You are not getting enough protein. Consider adding these high-protein dishes:",
            "dishes": [{"name": d.name, "id": d.id, "type": d.type,  "protein": d.protein_100} for d in dishes]
        })

    if fiber_ratio < 0.8:
        dishes = Dish.objects.filter(fiber_100__gt=8).order_by("-fiber")[:5]
        suggestions.append({
            "message": "You're low on fiber. These fiber-rich dishes may help:",
            "dishes": [{"name": d.name, "id": d.id, "type": d.type,  "fiber": d.fiber_100} for d in dishes]
        })

    if sugar_ratio > 1.2:
        dishes = Dish.objects.filter(sugars_100__lt=5).order_by("sugars")[:5]
        suggestions.append({
            "message": "You consume a lot of sugar. Try replacing with these lower-sugar dishes:",
            "dishes": [{"name": d.name, "id": d.id, "type": d.type,  "sugars": d.sugars_100} for d in dishes]
        })

    if caffeine_ratio > 1.2:
        suggestions.append({
            "message": "You are consuming a lot of caffeine. This may be dangerous for your heart. Consider drinking less coffee, energy drinks and tea:",
            "dishes": []
        })

    if not suggestions:
        dishes = Dish.objects.all().order_by("?")[:3]
        suggestions.append({
            "message": "You're doing great overall! Here are some dishes to explore anyway:",
            "dishes": [{"name": d.name, "id": d.id, "type": d.type, } for d in dishes]
        })

    return suggestions
