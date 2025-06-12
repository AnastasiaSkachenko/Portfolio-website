from backend.models import IngredientOld, Ingredient

for ing in IngredientOld.objects.all():
    Ingredient.objects.create(
        product=ing.product,
        calories=ing.calories,
        protein=ing.protein,
        carbohydrate=ing.carbohydrate,
        fat=ing.fat,
        fiber=ing.fiber,
        sugars=ing.sugars,
        caffeine=ing.caffeine,
        dish=ing.dish,
        weight=ing.weight,
        name=ing.name,
    )
