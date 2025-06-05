# Example script to migrate data and create mapping
from backend.models import  Product, Dish, Ingredient


for dish in Dish.objects.all():
    if dish.product:
        try:
            matched_product = Product.objects.get(name=dish.product.name)
            dish.product_uuid = matched_product
            dish.save()
        except Product.DoesNotExist:
            print(f"New Product not found for name: {dish.product.name}")

for ingredient in Ingredient.objects.all():
    if ingredient.product:
        try:
            matched_product = Product.objects.get(name=ingredient.product.name)
            ingredient.product_uuid = matched_product
            ingredient.save()
        except Product.DoesNotExist:
            print(f"New Product not found for name: {ingredient.product.name}")
