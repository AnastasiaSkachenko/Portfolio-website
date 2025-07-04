from rest_framework.response import Response
from backend.models import Dish, Ingredient, Product, DishMedia
from backend.serializers import DishSerializer, IngredientSerializer, DishMediaSerializer
from rest_framework.views import APIView
from rest_framework import  status 
from django.db.models import Sum  
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.paginator import Paginator
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from backend.authentication import customJWTAuthentication
from django.http import HttpResponseForbidden
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.utils.dateparse import parse_datetime 


class GetAllDishes(APIView): 
    permission_classes = []

    def get(self, request):
        try:
            dishes = Dish.objects.filter(is_deleted=False)
            dishes_data = DishSerializer(dishes, many=True).data

            media_qs = DishMedia.objects.filter(dish__in=dishes)
            media_dict = {}

            for media in media_qs:
                media_data = DishMediaSerializer(media).data
                dish_id_str = str(media.dish.id)
                if dish_id_str not in media_dict:
                    media_dict[dish_id_str] = []
                media_dict[dish_id_str].append(media_data)

            # Attach media
            for dish in dishes:
                dish['media'] = media_dict.get(str(dish['id']), [])


            print(len(dishes_data), 'dishes send when pulling dishes')
            return Response({"dishes": dishes_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to fetch dishes"}, status=status.HTTP_400_BAD_REQUEST)



class GetUpdatedDishes(APIView):
    permission_classes = []

    def get(self, request):
        last_synced = request.query_params.get('last_synced')
        if not last_synced:
            return Response({"error": "last_synced query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        last_synced_dt = parse_datetime(last_synced)
        if not last_synced_dt:
            return Response({"error": "Invalid datetime format for last_synced"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch updated dishes and deleted ones
        dishes = Dish.objects.filter(last_updated__gt=last_synced_dt, is_deleted=False)

        media_qs = DishMedia.objects.filter(dish__in=dishes)
        media_dict = {}

        for media in media_qs:
            media_data = DishMediaSerializer(media).data
            dish_id_str = str(media.dish.id)
            if dish_id_str not in media_dict:
                media_dict[dish_id_str] = []
            media_dict[dish_id_str].append(media_data)

        # Attach media
        for dish in dishes:
            dish['media'] = media_dict.get(str(dish['id']), [])


        deleted_dishes = list(Dish.objects.filter(is_deleted=True).values_list('id', flat=True))

        serializer = DishSerializer(dishes, many=True)
        return Response({
            "dishes": serializer.data,
            "deleted_dishes": deleted_dishes
        }, status=status.HTTP_200_OK)




class DishView(APIView): 
    permission_classes = []
    authentication_classes = [customJWTAuthentication]

    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        user = request.user  # Get the current user
        dishes = Dish.objects.filter(is_deleted=False).order_by('-last_updated')

        # Filtering options
        query = request.query_params.get('query', None)
        page = request.query_params.get('page', 1)
        only_no_product = request.query_params.get('only_no_product', 'false').lower() == 'true'
        filters = request.query_params.getlist('filter[]') 
        print(filters, 'filters')
        print(request.GET, 'request.GET')
        print(request.query_params, 'request.query_params')

        # Start with a queryset
 
        if only_no_product:
            dishes = dishes.filter(product__isnull=True)

        if query:
            dishes = dishes.filter(name__icontains=query)

        if 'favorites' in filters:
            if not user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access favorite dishes.")
            favorite_dish_ids = user.favorite_dishes.values_list("id", flat=True)
            dishes = dishes.filter(id__in=favorite_dish_ids)

        if 'custom' in filters:
            dishes = dishes.filter(type="custom")

        if 'pre_made' in filters:
            dishes = dishes.filter(type="pre_made")

        if 'own' in filters:
            if not user.is_authenticated:
                return HttpResponseForbidden("You must be logged in to access own dishes.")
            dishes = dishes.filter(user=user)

        if 'high_protein' in filters:
            dishes = dishes.filter(protein_100__gt=15)

        if 'low_carbs' in filters:
            dishes = dishes.filter(carbs_100__lt=10)

        if 'low_fat' in filters:
            dishes = dishes.filter(fat_100__lt=3)

        if 'suggestions' in filters:
            # You override all filters here
            dishes = Dish.objects.filter(is_popular=True).order_by('-id')


        # Pagination
        page_size = 20
        paginator = Paginator(dishes, page_size)
        try:
            paginated_dishes = paginator.page(page)
        except:
            return Response({"error": "Invalid page number"}, status=status.HTTP_400_BAD_REQUEST)

        dish_data = DishSerializer(paginated_dishes, many=True).data

        if user.is_authenticated:
            # Get favorite dish IDs for the current user if authenticated
            favorite_dish_ids = set(user.favorite_dishes.values_list("id", flat=True))
            # Attach the 'favorite' field to each dish
            for dish in dish_data:
                dish['favorite'] = dish['id'] in favorite_dish_ids  # Add favorite field
        else:
            # If the user is not authenticated, do not include the 'favorite' field
            for dish in dish_data:
                dish['favorite'] = False

        # Optimize ingredient fetching with bulk queries
        dish_ids = [str(dish['id']) for dish in dish_data]

        ingredients = Ingredient.objects.filter(dish__id__in=dish_ids, is_deleted=False).select_related('product')
        ingredient_dict = {}

        for ingredient in ingredients:
            ingredient_data = IngredientSerializer(ingredient).data
            if ingredient.product:
                ingredient_data['name'] = ingredient.product.name

            dish_id_str = str(ingredient.dish.id)  # Normalize UUID to string
            if dish_id_str not in ingredient_dict:
                ingredient_dict[dish_id_str] = []

            ingredient_dict[dish_id_str].append(ingredient_data)

        # Attach ingredients using string IDs
        for dish in dish_data:
            dish['ingredients'] = ingredient_dict.get(str(dish['id']), [])

        # Optimize media fetching
        media_qs = DishMedia.objects.filter(dish__id__in=dish_ids, is_deleted=False)
        media_dict = {}

        for media in media_qs:
            media_data = DishMediaSerializer(media).data
            dish_id_str = str(media.dish.id)
            if dish_id_str not in media_dict:
                media_dict[dish_id_str] = []
            media_dict[dish_id_str].append(media_data)

        # Attach media
        for dish in dish_data:
            dish['media'] = media_dict.get(str(dish['id']), [])

        


        return Response({
            "dishes": dish_data,
            "has_more": paginated_dishes.has_next()
        }, status=status.HTTP_200_OK)

    def post(self, request, format=False):
        data = request.data.dict()
        print(data)

        # Uniqueness check
        productExists = Product.objects.filter(name=data.get('name')).exists()
        dishExists = Dish.objects.filter(name=data.get('name')).exists()
        if productExists or dishExists:
            return Response({"error": 'Product or dish with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DishSerializer(data=data)

        if serializer.is_valid():
            dish = serializer.save()

            # Save multiple media files
            files = request.FILES.getlist('files')  # 👈 getlist to support multiple uploads
            for file in files:
                DishMedia.objects.create(dish=dish, file=file)

            return Response({"id": dish.id}, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=False):
        dish_id = request.query_params.get('id')
        try:
            dish = Dish.objects.get(id=dish_id)
        except Dish.DoesNotExist:
            return Response({"error": "Dish not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.dict()

        serializer = DishSerializer(dish, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Save any new media files
            files = request.FILES.getlist('files')
            for file in files:
                DishMedia.objects.create(dish=dish, file=file)

            return Response({"message": "Dish updated successfully"}, status=status.HTTP_200_OK)

        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): 
        dish_id = request.query_params.get('id')

        try:
            dish = Dish.objects.get(id=dish_id)
            dish.is_deleted = True
            dish.save()

            return Response({"message": "Dish deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Dish.DoesNotExist:
            return Response({"error": "Dish not found"}, status=status.HTTP_404_NOT_FOUND)


class GetDishNames(APIView):
    permission_classes = []
    def get(self, request):
        dish_names = Dish.objects.values_list('name', flat=True)  # Returns a flat list
        return Response({"dishes": dish_names,}, status=200)



class IsNameUnique(APIView):
    permission_classes = [AllowAny]  

    def get(self, request):
        name = request.query_params.get('name')
        editing_name = request.query_params.get('editingName')

        if not name:
            return Response({"error": "Name is required"}, status=400)

        # Check uniqueness, but ignore if the name matches the editingName
        exists_product = Product.objects.filter(name__iexact=name).exclude(name__iexact=editing_name).exists()
        exists_dish = Dish.objects.filter(name__iexact=name).exclude(name__iexact=editing_name).exists()

        print(exists_dish, exists_product)
        return Response({"exists_product": exists_product, "exists_dish": exists_dish}, status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def getDishById(request, id):
    try:
        dish = Dish.objects.get(id=id)
    except Dish.DoesNotExist:
        return Response({"error": "Dish not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DishSerializer(dish)
    dish_data = serializer.data   

    ingredients = Ingredient.objects.filter(dish=dish)
    ingredient_list = []

    for ingredient in ingredients:
        ingredient_data = IngredientSerializer(ingredient).data
        if ingredient.product:
            ingredient_data['name'] = ingredient.product.name
        ingredient_list.append(ingredient_data)

    dish_data['ingredients'] = ingredient_list

    if request.user.is_authenticated:
        favorite_dish_ids = set(request.user.favorite_dishes.values_list("id", flat=True))
        dish_data['favorite'] = dish.id in favorite_dish_ids
    else:
        dish_data['favorite'] = False

    return Response(dish_data)

def recalculate_dish(dish_id):
    dish = Dish.objects.get(id=dish_id)

    # Aggregate the related ingredient data
    aggregated_data = dish.ingredientsDish.aggregate(
        total_weight=Sum('weight'),
        total_calories=Sum('calories'),
        total_protein=Sum('protein'),
        total_carbs=Sum('carbs'),
        total_fat=Sum('fat'),
    )

    # Convert to Decimal and round to 1 decimal place
    def round_decimal(value):
        return Decimal(value or 0).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

    dish.weight = round_decimal(aggregated_data['total_weight'])
    dish.calories = round_decimal(aggregated_data['total_calories'])
    dish.protein = round_decimal(aggregated_data['total_protein'])
    dish.carbs = round_decimal(aggregated_data['total_carbs'])
    dish.fat = round_decimal(aggregated_data['total_fat'])
    dish.save()

    # Calculate per 100g values
    base_weight = dish.weight_of_ready_product or dish.weight
    if base_weight > 0:
        dish.calories_100 = round_decimal(dish.calories / base_weight * 100)
        dish.protein_100 = round_decimal(dish.protein / base_weight * 100)
        dish.carbs_100 = round_decimal(dish.carbs / base_weight * 100)
        dish.fat_100 = round_decimal(dish.fat / base_weight * 100)
    else:
        dish.calories_100 = Decimal(0)
        dish.protein_100 = Decimal(0)
        dish.carbs_100 = Decimal(0)
        dish.fat_100 = Decimal(0)

    dish.save()


class ToggleFavorite(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]

    def patch(self, request, dish_id):
        """Toggle the favorite status of a dish for the authenticated user."""
        user = request.user
        print(user, 'user toggle')
        dish = get_object_or_404(Dish, id=dish_id)
        
        is_favorite = user.toggle_favorite(dish)  # Call the method on User

        return Response({"dish_id": dish_id, "favorite": is_favorite})
