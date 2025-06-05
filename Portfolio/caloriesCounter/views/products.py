from django.http import JsonResponse
from rest_framework.response import Response
from backend.models import Product, Dish
from backend.serializers import ProductSerializer
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
            products = Product.objects.all().order_by('-id')
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
            products = Product.objects.all().order_by('-id')

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
    
    def post(self, request, format=None ):
        
        data = request.data.dict()
        if 'image' in request.FILES:
            print('image is in files')
            data['image'] = request.FILES['image']

        
        productExists = Product.objects.filter(name=data.get('name'))
        dishExists = Dish.objects.filter(name=data.get('name'))
        if productExists or dishExists:
            print(productExists[0].name)
            print(dishExists[0].name, 'dish')
            return JsonResponse({"error": 'Product or dish with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)


        for field in ['calories', 'protein', 'carbohydrate', 'fat', 'fiber', 'sugars', 'caffein']:
            if data.get(field) == '':
                data[field] = 0

        print(data, 'data')

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
                weight=100,
            )
        
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):

        id = request.query_params.get('id')

        product = get_object_or_404(Product, id=id)
        data = request.data.dict()
        print(data.get('calories'), 'calories')
        for field in ['calories', 'protein', 'carbohydrate', 'fat', 'fiber', 'sugars', 'caffein']:
            if data.get(field) == '':
                data[field] = 0
        
        if 'image' in request.FILES:
            print('image is in files')
            data['image'] = request.FILES['image']


        print(data, 'data')

        serializer = ProductSerializer(product, data=data, partial=True)

        if serializer.is_valid():
            instance = serializer.save() 
            dish = Dish.objects.get(product=instance)
 
            # Update Dish fields based on the Product instance
            dish.name = instance.name  # Example: Updating name if needed
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

        # Assuming you have a ProductSerializer
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data}, status=status.HTTP_200_OK)

class CheckProductExistsView(APIView):
    permission_classes = [AllowAny]  # Publicly accessible

    def get(self, request):
        product_name = request.query_params.get('name')

        if not product_name:
            return Response({"error": "Product name is required"}, status=400)

        exists = Product.objects.filter(name__iexact=product_name).exists()

        return Response({"exists": exists}, status=200)

