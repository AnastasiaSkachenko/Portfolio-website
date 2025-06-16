from backend.models import DailyGoals, DailyGoalsOLD
import uuid

goals_to_create = []

for goal in DailyGoalsOLD.objects.all():
    goals_to_create.append(
        DailyGoals(
            id=uuid.uuid4(),
            user=goal.user,
            date=goal.date,
            calories_burned=goal.calories_burned,
            calories_burned_goal=goal.calories_burned_goal,
            protein=goal.protein,
            protein_goal=goal.protein_goal,
            carbohydrate=goal.carbohydrate,
            carbohydrate_goal=goal.carbohydrate_goal,
            fat=goal.fat,
            fat_goal=goal.fat_goal,
            fiber=goal.fiber,
            fiber_goal=goal.fiber_goal,
            sugars=goal.sugars,
            sugars_goal=goal.sugars_goal,
            caffeine=goal.caffeine,
            caffeine_goal=goal.caffeine_goal,
            calories_intake=goal.calories_intake,
            calories_intake_goal=goal.calories_intake_goal,
        )
    )

DailyGoals.objects.bulk_create(goals_to_create)
