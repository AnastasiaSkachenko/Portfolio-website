from rest_framework.response import Response
from rest_framework.decorators import api_view
from backend.models import  Dish, Ingredient
from backend.serializers import ProductSerializer, IngredientSerializer
from rest_framework.views import APIView
from rest_framework import  status 
from django.shortcuts import get_object_or_404 
from django.utils import timezone
from rest_framework.exceptions import NotFound
from .dishes import recalculate_dish
from django.utils.dateparse import parse_datetime 


class GetAllIngredients(APIView): 
    permission_classes = []

    def get(self, request):
        try:
            ingredients = Ingredient.objects.filter(is_deleted=False).order_by('-id')
            ingredients_data = IngredientSerializer(ingredients, many=True).data
            return Response({"ingredients": ingredients_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to fetch ingredients"}, status=status.HTTP_400_BAD_REQUEST)


class GetUpdatedIngredients(APIView):
    permission_classes = []

    def get(self, request):
        last_synced = request.query_params.get('last_synced')
        if not last_synced:
            return Response({"error": "last_synced query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        last_synced_dt = parse_datetime(last_synced)
        if not last_synced_dt:
            return Response({"error": "Invalid datetime format for last_synced"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch updated dishes and deleted ones
        ingredients = Ingredient.objects.filter(last_updated__gt=last_synced_dt, is_deleted=False)
        deleted_ingredients = list(Ingredient.objects.filter(is_deleted=True).values_list('id', flat=True))

        serializer = IngredientSerializer(ingredients, many=True)
        return Response({
            "ingredients": serializer.data,
            "deleted_ingredients": deleted_ingredients
        }, status=status.HTTP_200_OK)


class IngredientView(APIView): 
    permission_classes = []

    def get(self,request, id):
        try:
            ingredient = Ingredient.objects.filter(id=id, is_deleted=False)
        except Ingredient.DoesNotExist:
            raise NotFound("Ingredient not found.")

        ingredient_serialized = IngredientSerializer(ingredient).data
        ingredient_serialized.name = ingredient.product.name
        
        # Serialize the product
        product = ingredient.product
        product_serialized = ProductSerializer(product).data

        # Combine ingredient and product data
        response_data = {
            "ingredient": ingredient_serialized,
            "product": product_serialized
        }
        return Response(response_data)
    
    def post(self, request):
        data = request.data.copy()
        print('data', data)
        dish = data.get('dish')

        for field in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugars', 'caffein']:
            if data.get(field) == '':
                data[field] = 0
# temporary

        data['dish_old'] = 9

        serializer = IngredientSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            
            recalculate_dish(dish)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request, id): 
        ingredient = get_object_or_404(Ingredient, id=id) 
        data = request.data.copy()

        for field in ['calories', 'protein', 'carbohydrate', 'fat', 'fiber', 'sugars', 'caffein']:
            if data.get(field) == '':
                data[field] = 0


        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)

        recalculate_dish(ingredient.dish.id)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        serializer.save()

        return Response({"message": "ingredient updated successfully", "product": serializer.data}, status=status.HTTP_200_OK)
        
    def delete(self, request, id): 
        ingredient = Ingredient.objects.get(id=id)
        ingredient.is_deleted = True
        ingredient.save()
        
        recalculate_dish(ingredient.dish.id)              
        return Response({"message": "TC product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def getIngredientsInDish(request):
    dishes = Dish.objects.all()
    ingredientsAll = {}

    for dish in dishes:
        ingredients = Ingredient.objects.filter(dish=dish.id, is_deleted=False)
        
        if not ingredients.exists():  # Skip the dish if no ingredients are found
            continue

        data = []
        for ingredient in ingredients:
            ingredient_serialized = {
                'id': ingredient.id,
                'name': ingredient.product.name,
                'calories': ingredient.calories,
                'protein': ingredient.protein,
                'carbohydrate': ingredient.carbohydrate,
                'fat': ingredient.fat,
                'product': ingredient.product.id,
                'weight': ingredient.weight
            }
            data.append(ingredient_serialized)
        
        ingredientsAll[dish.id] = data  # Add data only for dishes with ingredients
    return Response({'ingredients': ingredientsAll}, status=status.HTTP_200_OK)



