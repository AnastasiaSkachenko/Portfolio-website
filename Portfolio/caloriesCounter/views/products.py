from django.http import JsonResponse
from rest_framework.response import Response
from backend.models import Product, Dish
from backend.serializers import ProductSerializer, DishSerializer
from rest_framework.views import APIView
from rest_framework import  status 
from django.shortcuts import get_object_or_404 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.utils.dateparse import parse_datetime 



class GetAllProducts(APIView): 
    permission_classes = []

    def get(self, request):
        try:
            products = Product.objects.filter(is_deleted=False).order_by('-id')
            products_data = ProductSerializer(products, many=True).data


            return Response({"products":products_data}, status=200)
        except:
            return Response({"error": 'Failed to fetch products'}, status=status.HTTP_400_BAD_REQUEST)



def ping(request):
    return JsonResponse({"status": "ok"})


class ProductView(APIView): 
    permission_classes = []

    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        try:
            products = Product.objects.filter(is_deleted=False).order_by('-last_updated')

            page = request.query_params.get('page')
            query = request.query_params.get('query')

            if query:
                starts_with_products = products.filter(name__istartswith=query)
                contains_products = products.filter(name__icontains=query).exclude(id__in=starts_with_products.values_list('id', flat=True))
                products = starts_with_products | contains_products

            if page:
                page = int(page)
                page_size = 30
                start = (page - 1) * page_size
                end = page * page_size

                paginated_products = products[start:end]
                has_more = end < products.count()
            else:
                paginated_products = products
                has_more = False

            products_data = ProductSerializer(paginated_products, many=True).data

            return Response({"products": products_data, "has_more": has_more}, status=200)
        except:
            return Response({"error": 'Failed to fetch products'}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        print('request.data', request.data)

        product_data = {}
        dish_data = {}

        for key, value in request.data.items():
            if key.startswith('product_'):
                product_data[key.replace('product_', '')] = value
            elif key.startswith('dish_'):
                dish_data[key.replace('dish_', '')] = value

        # Handle file separately
        if 'product_image' in request.FILES:
            product_data['image'] = request.FILES['product_image']
        if 'dish_image' in request.FILES:
            dish_data['image'] = request.FILES['dish_image']

        for field in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugars', 'caffeine']:
            if product_data.get(field) == '':
                product_data[field] = 0

        print(product_data, 'product data')
        serializer = ProductSerializer(data=product_data)

        if serializer.is_valid():
            product_instance = serializer.save()
            source = request.headers.get("X-App-Source")
            if source == "web":
                Dish.objects.create(
                    product=product_instance,
                    name=product_data.get('name'),
                    image=product_instance.image,
                    calories=product_data.get('calories', 0),
                    calories_100=product_data.get('calories', 0),
                    protein=product_data.get('protein', 0),
                    protein_100=product_data.get('protein', 0),
                    carbs=product_data.get('carbs', 0),
                    carbs_100=product_data.get('carbs', 0),
                    sugars=product_data.get('sugars', 0),
                    sugars_100=product_data.get('sugars', 0),
                    fiber=product_data.get('fiber', 0),
                    fiber_100=product_data.get('fiber', 0),
                    caffeine=product_data.get('caffeine', 0),
                    caffeine_100=product_data.get('caffeine', 0),
                    fat=product_data.get('fat', 0),
                    fat_100=product_data.get('fat', 0),
                    weight=100,
                )
            else:
                dish_data['product'] = product_instance.id
                dish_serializer = DishSerializer(data=dish_data)
                if not dish_serializer.is_valid():
                    print(dish_serializer.errors)
                    return JsonResponse({"message": "Failed to create dish"}, status=status.HTTP_400_BAD_REQUEST)
                dish_serializer.save()

            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        product_id = request.query_params.get('id')
        product = get_object_or_404(Product, id=product_id)

        # Flatten the form data
        raw_data = request.data.copy()  # QueryDict to mutable dict
        product_data = {}
        dish_data = {}

        # Separate product_ and dish_ fields
        for key, value in raw_data.items():
            if key.startswith("product_"):
                product_data[key.replace("product_", "")] = value
            elif key.startswith("dish_"):
                dish_data[key.replace("dish_", "")] = value

        # Handle image file for product
        if 'product_image' in request.FILES:
            product_data['image'] = request.FILES['product_image']

        # Replace empty string with 0 for numeric fields
        for field in ['calories', 'protein', 'carbohydrate', 'fat', 'fiber', 'sugars', 'caffein']:
            if product_data.get(field) == '':
                product_data[field] = 0

        # Update Product
        serializer = ProductSerializer(product, data=product_data, partial=True)

        if serializer.is_valid():
            product_instance = serializer.save()
            source = request.headers.get("X-App-Source")

            if source == "web":
                # Update corresponding dish fields from updated product
                dish = Dish.objects.get(product=product_instance)
                dish.name = product_instance.name
                dish.calories = product_instance.calories
                dish.calories_100 = product_instance.calories
                dish.protein = product_instance.protein
                dish.protein_100 = product_instance.protein
                dish.carbs = product_instance.carbs
                dish.carbs_100 = product_instance.carbs
                dish.fat = product_instance.fat
                dish.fat_100 = product_instance.fat
                dish.sugars = product_instance.sugars
                dish.sugars_100 = product_instance.sugars
                dish.fiber = product_instance.fiber
                dish.fiber_100 = product_instance.fiber
                dish.caffeine = product_instance.caffeine
                dish.caffeine_100 = product_instance.caffeine
                dish.save()
            else:
                # Mobile: update dish using nested dish form data
                dish_id = dish_data.get('id')
                if not dish_id:
                    return Response({"message": "Dish ID is required."}, status=status.HTTP_400_BAD_REQUEST)

                current_dish = get_object_or_404(Dish, id=dish_id)
                dish_serializer = DishSerializer(current_dish, data=dish_data, partial=True)

                if not dish_serializer.is_valid():
                    return Response({"message": "Failed to update dish", "errors": dish_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                dish_serializer.save()

            return Response({"message": "Product updated successfully", "product": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        id = request.query_params.get('id')

        product = get_object_or_404(Product, id=id)    
        dish = Dish.objects.filter(product=product).first()
        if dish:
            dish.is_deleted = True
            dish.save()
        product.is_deleted = True
        product.save()
        
        return Response({"message": "Product marked as  deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class GetProductNames(APIView):
    permission_classes = []

    def get(self, request):
        product_names = Product.objects.values_list('name', flat=True)  # Returns a flat list
        return Response({"products": product_names}, status=200)




class GetUpdatedProducts(APIView):
    permission_classes = []  

    def get(self, request):
        last_synced = request.query_params.get('last_synced')
        if not last_synced:
            return Response({"error": "last_synced query param is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # parse the string datetime to Python datetime object
        last_synced_dt = parse_datetime(last_synced)
        if not last_synced_dt:
            return Response({"error": "Invalid datetime format for last_synced"}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(last_updated__gt=last_synced_dt)
        deleted_products = list(Product.objects.filter(is_deleted=True).values_list('id', flat=True))

        # Assuming you have a ProductSerializer
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data, "deleted_products": deleted_products}, status=status.HTTP_200_OK)

class CheckProductExistsView(APIView):
    permission_classes = [AllowAny]  # Publicly accessible

    def get(self, request):
        product_name = request.query_params.get('name')

        if not product_name:
            return Response({"error": "Product name is required"}, status=400)

        exists = Product.objects.filter(name__iexact=product_name).exists()

        return Response({"exists": exists}, status=200)

