from rest_framework.views import APIView
from rest_framework import status, generics
from backend.serializers import UserSerializer, RegisterSerializer, ResetPasswordSerializer, EmailSerializer, VerifyCodeSerializer
from rest_framework.permissions import IsAuthenticated
from backend.models import User
from rest_framework import status 
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from backend.authentication import customJWTAuthentication
from rest_framework.permissions import AllowAny
import random
import string
from django.core.cache import cache
from django.core.mail import send_mail
from ..tasks import update_calories_balance, update_popular_dishes
from rest_framework.parsers import MultiPartParser, FormParser



class TestingHere(APIView):
    permission_classes = []
    authentication_classes = []
    def post(self, request):
        update_calories_balance()
        #update_popular_dishes()
        return Response({"testing here": 'right here'}, status=status.HTTP_200_OK)




# Registration View
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save and create the user profile
            return Response({'message': 'User created successfully!',}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User was not created!',}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login View
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        # Extract refresh token and remove it from response body
        refresh_token = data.pop("refresh", None)  
        access_token = data.get("access")

        # Get user info
        user = request.user  # This might not work, use workaround below
        if user and user.is_authenticated:
            user_data = UserSerializer(user).data
        else:
            from django.contrib.auth import authenticate
            email = request.data.get("email")
            password = request.data.get("password")
            user = authenticate(request, email=email, password=password)
            user_data = UserSerializer(user).data if user else {}

        # Create a new response with access token and user info
        response_data = {
            "access": access_token,
            "user": user_data,  # ✅ Include user details
            "refresh": refresh_token 
        }


        response = Response(response_data, status=status.HTTP_200_OK)

        # Set the refresh token as an HTTP-only cookie
        if refresh_token:
            response.set_cookie(
                key="refresh",
                value=refresh_token,
                httponly=True,  # Prevents JavaScript access
                secure=True,   # Set to True in production (HTTPS required)
                samesite="None",  # Needed for cross-origin requests
             )

        return response

# Refresh token View
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh")
        if not  refresh_token:
            print(request.headers.get('Authorization'), 'headers')
            authorization_header = request.headers.get('Authorization')
            if authorization_header:
                refresh_token = authorization_header.split(" ")[1]  # Extract the token from "Bearer <token>"

        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except Exception:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({"access": access_token,"refresh": refresh_token}, status=status.HTTP_200_OK)

# Fetch user View
class GetUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]  

    def get(self, request):

        access_token = request.headers.get("Authorization")
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            refresh_token = request.data.get('refresh')

        print(request.headers.get('refresh'), 'headers should be printed')

        user = None  # Initialize user variable
        new_access_token = None  # Store new access token if refreshed

        if access_token and access_token.startswith("Bearer "):
            try:
                token_str = access_token.split(" ")[1]  # Extract the token from "Bearer <token>"
                decoded_token = AccessToken(token_str)
                user_id = decoded_token["user_id"]
                user = User.objects.get(id=user_id)
            except Exception:
                pass  # Invalid access token, try refresh token

        if not user and refresh_token:
            try:
                refresh = RefreshToken(refresh_token)
                new_access_token = str(refresh.access_token)  
                user_id = refresh["user_id"]
                user = User.objects.get(id=user_id)
            except Exception:
                return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user:
            return Response({"error": "No valid authentication provided"}, status=status.HTTP_401_UNAUTHORIZED)

        favorite_dish_ids = user.favorite_dishes.values_list("id", flat=True)

        # Response with user info and new access token (if refreshed)
        response_data = {
            "user": UserSerializer(user).data,
            "favoriteDishes": list(favorite_dish_ids),
        }


        if new_access_token:
            response_data["access"] = new_access_token  # Send access token in response headers
        else:
            response_data["access"] = access_token[7:]
        response = Response(response_data, headers={"Authorization": f"Bearer {new_access_token}"} if new_access_token else {})

        return response

# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]  

    def post(self, request):
        try:

            refresh_token = request.COOKIES.get("refresh")

            if not refresh_token:
                refresh_token = request.headers.get("refresh")
                print(request.headers, 'headers')



            if not refresh_token:
                print('no refresh token')
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Remove the refresh token from cookies
            response = Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
            response.set_cookie(
                key="refresh",
                value='',
                httponly=True,  # Prevents JavaScript access
                secure=True,   # Set to True in production (HTTPS required)
                samesite="None",  # Needed for cross-origin requests
                max_age=10  # 7 days expiration
            )

            return response

        except Exception as e:
            print(e, 'errro')
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# Modify User View

class ModifyUserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]  
    parser_classes = (MultiPartParser, FormParser)  # Allow handling file uploads

    def put(self, request, format=None):
        user = request.user
        recalculate = request.query_params.get('recalculate')

        # Use request.data directly, no need to copy
        data = request.data.dict()  # Convert QueryDict to normal dict

        # Handle image upload properly
        if 'image' in request.FILES:
            data['image'] = request.FILES['image']

        serializer = UserSerializer(user, data=data, partial=True)

        if serializer.is_valid():
            user = serializer.save()

            if recalculate == 'true':
                user = calculate_macros_for_user(user)  # Ensure this modifies and saves the user

            updated_serializer = UserSerializer(user)  
            return Response({"message": "Profile updated successfully", "user": updated_serializer.data})        
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# function for calculating macros for for for user
def calculate_macros_for_user(user):
    """
    Calculate macros for a given user instance and update the user object.
    """
    age = user.age
    weight = user.weight
    height = user.height
    activity_level = user.activity_level
    gender = user.gender
    goal = user.goal

    # Calculate BMR using Mifflin-St Jeor Equation
    if gender == "female":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5

    # Activity level multipliers
    activity_multipliers = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
    activity_multiplier = activity_multipliers.get(activity_level, 1.2)

    # Calculate TDEE
    total_calories = round(bmr * activity_multiplier)

    # Adjust calories based on goal
    goal_multipliers = {
        "fat_loss": 0.85, "active_fat_loss": 0.75, 
        "muscle_gain": 1.15, "active_muscle_gain": 1.25, 
        "maintenance": 1.0
    }
    total_calories = round(total_calories * goal_multipliers.get(goal, 1.0))

    # Adjust protein intake based on goal
    protein_targets = {
        "fat_loss": 2.2, "active_fat_loss": 2.4, 
        "muscle_gain": 2.4, "active_muscle_gain": 2.6, 
        "maintenance": 1.6
    }
    protein_per_kg = protein_targets.get(goal, 1.6)
    protein_d = round(weight * protein_per_kg)
    protein_calories = protein_d * 4  # 1g protein = 4 kcal

    # Adjust fat intake as a percentage of total calories
    fat_ratios = {
        "fat_loss": 0.25, "active_fat_loss": 0.22,
        "muscle_gain": 0.22, "active_muscle_gain": 0.22,
        "maintenance": 0.25
    }
    fat_ratio = fat_ratios.get(goal, 0.25)
    fat_d = round((total_calories * fat_ratio) / 9)  # 1g fat = 9 kcal
    fat_calories = fat_d * 9

    # Carbohydrates: Remaining calories after protein & fat
    remaining_calories = total_calories - (protein_calories + fat_calories)
    carbohydrate_d = round(remaining_calories / 4)  # 1g carb = 4 kcal

    # Update user instance
    user.calories_d = total_calories
    user.protein_d = protein_d
    user.carbohydrate_d = carbohydrate_d
    user.fat_d = fat_d
    user.save()

    return user




#                                                                                      reset password logic
def generate_verification_code():
    """Generate a 6-digit random code."""
    return ''.join(random.choices(string.digits, k=6))

def store_verification_code(email, code, timeout=300):
    """Store the verification code in cache for 5 minutes (default)."""
    cache.set(f"verification_code_{email}", code, timeout)

def get_stored_verification_code(email):
    """Retrieve the stored verification code."""
    return cache.get(f"verification_code_{email}")

def delete_verification_code(email):
    """Remove the verification code after successful verification."""
    cache.delete(f"verification_code_{email}")




class SendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = generate_verification_code()
            store_verification_code(email, code)

            # Send email
            send_mail(
                subject="Your Verification Code",
                message=f"Your verification code is: {code}",
                from_email="your@email.com",
                recipient_list=[email],
                fail_silently=False,
            )

            return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            code = serializer.validated_data["code"]

            stored_code = get_stored_verification_code(email)
            if stored_code and stored_code == code:
                delete_verification_code(email)
                return Response({"message": "Verification successful."}, status=status.HTTP_200_OK)

            return Response({"message": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
 
 
            serializer.save(serializer.validated_data)
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
