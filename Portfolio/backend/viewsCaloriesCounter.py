from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, Dish, Ingredient, DiaryRecord
from .serializers import ProductSerializer, DishSerializer, IngredientSerializer, DiarySerializer
from rest_framework.views import APIView
from rest_framework import  status 
from django.shortcuts import get_object_or_404 
from django.db.models import Sum  
from django.utils import timezone
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser, FormParser


class ProductView(APIView): 
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        products = Product.objects.all().order_by('-id')

        page = request.query_params.get('page')

        if page:
            query = request.query_params.get('query')
            if query:
                products = products.filter(name__icontains=query)
            page = int(page)
            page_size = 30
            start = (page - 1) * page_size
            end = page * page_size

            paginated_products = products[start:end]
            has_more = end < products.count()
            products_data = ProductSerializer(paginated_products, many=True).data
        else:
            products_data = ProductSerializer(products, many=True).data
            has_more = False

        return Response({ "products": products_data, "has_more": has_more}, status=200)      
    
    def post(self, request, format=None):
        print(request.data)
        
        data = request.data

        for field in ['calories', 'protein', 'carbohydrate', 'fat']:
            if data.get(field) == '':
                data[field] = 0


        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product_instance = serializer.save()   
            dish = Dish.objects.create(
                product=product_instance,
                name=data.get('name'), 
                image=product_instance.image,
                calories=data.get('calories', 0), 
                calories_100=data.get('calories', 0),
                protein=data.get('protein', 0),
                protein_100=data.get('protein', 0),
                carbohydrate=data.get('carbohydrate', 0),
                carbohydrate_100=data.get('carbohydrate', 0),
                fat=data.get('fat', 0),
                fat_100=data.get('fat', 0),
                weight=100  
            )
        
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
 
        print(serializer.errors) 
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):

        id = request.query_params.get('id')

        product = get_object_or_404(Product, id=id)
        data = request.data
        for field in ['calories', 'protein', 'carbohydrate', 'fat']:
            if data.get(field) == '':
                data[field] = 0
        
        data.update(request.FILES)


        serializer = ProductSerializer(product, data=data, partial=True)

        if serializer.is_valid():
            instance = serializer.save() 
            dish = Dish.objects.get(product=instance)
 
            # Update Dish fields based on the Product instance
            dish.name = instance.name  # Example: Updating name if needed
            dish.image = data.get('image')  # Example: Updating image if relevant
            dish.calories = instance.calories
            dish.calories_100 = instance.calories
            dish.protein = instance.protein
            dish.protein_100 = instance.protein
            dish.carbohydrate = instance.carbohydrate
            dish.carbohydrate_100 = instance.carbohydrate
            dish.fat = instance.fat
            dish.fat_100 = instance.fat
            dish.save()     
            return Response({"message": "Product updated successfully", "product": serializer.data}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        product = get_object_or_404(Product, id=id)    
        product.delete()
        
        return Response({"message": "Product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class IngredientView(APIView): 
    def get(self,request, id):
        try:
            ingredient = Ingredient.objects.get(id=id)
        except Ingredient.DoesNotExist:
            raise NotFound("Ingredient not found.")

        ingredient_serialized = IngredientSerializer(ingredient).data
        ingredient_serialized.name = ingredient.product.name
        print(ingredient_serialized)
        
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
        dish = data.get('dish')
        print(dish, 'dish id')
        print(data, 'data')

        for field in ['calories', 'protein', 'carbohydrate', 'fat']:
            if data.get(field) == '':
                data[field] = 0


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

        for field in ['calories', 'protein', 'carbohydrate', 'fat']:
            if data.get(field) == '':
                data[field] = 0


        serializer = IngredientSerializer(ingredient, data=request.data, partial=True)

        recalculate_dish(ingredient.dish.id)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        serializer.save()

        return Response({"message": "ingredient updated successfully", "product": serializer.data}, status=status.HTTP_200_OK)
        
    def delete(self, request, id): 
        ingredient = Ingredient.objects.get(id=id)
        
        ingredient.delete() 

        recalculate_dish(ingredient.dish.id)              
        return Response({"message": "TC product deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def getIngredientsInDish(request):
    dishes = Dish.objects.all()
    ingredientsAll = {}

    for dish in dishes:
        ingredients = Ingredient.objects.filter(dish=dish.id)
        
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


class DishView(APIView): 
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):  
        dishes = Dish.objects.all().order_by('-id')

        page = request.query_params.get('page')

        if page:
            page = int(page)
            dishes = dishes.filter(product__isnull=True)
            page_size = 20
            start = (page - 1) * page_size
            end = page * page_size

            paginated_dishes = dishes[start:end]
            has_more = end < dishes.count()
            dish_data = DishSerializer(paginated_dishes, many=True).data

            for dish in dish_data:
                ingredients = Ingredient.objects.filter(dish=dish.get('id'))


                serialized_ingredients = IngredientSerializer(ingredients, many=True).data

                # Add the product name to each serialized ingredient
                for serialized in serialized_ingredients:
                    product_data = Product.objects.get(id=serialized.get('product'))
                    if product_data: 
                        serialized['name'] = product_data.name

                # Attach the updated ingredients to the dish
                dish['ingredients'] = serialized_ingredients
        else:
            dish_data = DishSerializer( dishes, many=True).data
            has_more = False

        return Response({"dishes": dish_data, "has_more": has_more}, status=status.HTTP_200_OK)

    def post(self, request, format=False):
        data = request.data
        print(data)

        
        serializer = DishSerializer(data=data)
        
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data.get('id'), status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, format=False):
        id = request.query_params.get('id')

        dish = Dish.objects.get(id=id)
        request.data.update(request.FILES)
        print(request.data)

        serializer = DishSerializer(dish, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save() 
            return Response({"message": "dish updated successfully"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): 
        id = request.query_params.get('id')
 
        dish = Dish.objects.get(id=id)
 
        dish.delete()

        return Response({"message": "Dish deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def getDishById(request, id):
    try:
        dish = Dish.objects.get(id=id)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = DishSerializer(dish)

    return Response(serializer.data)  

def recalculate_dish(dish_id):
    dish = Dish.objects.get(id=dish_id)
    
    # Aggregate the related ingredient data
    aggregated_data = dish.ingredientsDish.aggregate(
        total_weight=Sum('weight'),
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbohydrate=Sum('carbohydrate'),
        total_fat=Sum('fat'),
    )
    
    # Update the dish fields
    dish.weight = aggregated_data['total_weight'] or 0
    dish.calories = aggregated_data['total_calories'] or 0
    dish.protein = aggregated_data['total_protein'] or 0
    dish.carbohydrate = aggregated_data['total_carbohydrate'] or 0
    dish.fat = aggregated_data['total_fat'] or 0
    dish.save()
    if dish.weight > 0:
        dish.calories_100 = dish.calories / dish.weight * 100
        dish.protein_100 = dish.protein / dish.weight * 100
        dish.carbohydrate_100 = dish.carbohydrate / dish.weight * 100
        dish.fat_100 = dish.fat / dish.weight * 100
    else:
        dish.calories_100 = 0
        dish.protein_100 = 0
        dish.carbohydrate_100 = 0
        dish.fat_100 = 0    
    dish.save()


class DiaryView(APIView): 
    def get(self, request):  
        records = DiaryRecord.objects.all()  # Get all records from the table
        serializer = DiarySerializer(records, many=True)  # Serialize multiple records
        return Response({'diaryRecords':serializer.data}, status=status.HTTP_200_OK)
 
    def post(self, request):
        data = request.data.copy()  
        data['date'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
      
        serializer = DiarySerializer(data=data)
         
        if serializer.is_valid(): 
            serializer.save()
            print('diary record created', serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id):
        record = DiaryRecord.objects.get(id=id)

        serializer = DiarySerializer(record, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save() 
            return Response({"message": "Diary record updated successfully"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):  
        record = DiaryRecord.objects.get(id=id)
 
        record.delete()

        return Response({"message": "Dish record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


