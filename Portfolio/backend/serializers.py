from rest_framework import serializers
from .models import Project, Skill, Product, Ingredient, Dish, DiaryRecord, User, ActivityRecord
from django.contrib.auth.hashers import make_password


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self, validated_data):
        email = validated_data["email"]
        new_password = validated_data["new_password"]
        user = User.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'tools'] 

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['name', 'image', 'experience'] 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'

class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'

class DiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryRecord
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'age', 'image', 'calories_d', 'protein_d', 'carbohydrate_d', 'fat_d', 'height', 'weight', 'activity_level', 'email', 'gender', 'goal', "balance"]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # Ensures password isn't returned in the response
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'age', 'email', 'password', 'image', 
                  'calories_d', 'protein_d', 'carbohydrate_d', 'fat_d', 
                  'height', 'weight', 'activity_level', 'gender', 'goal']

    def create(self, validated_data):
        # Extract password before creating the user
        password = validated_data.pop('password')
        
        # Create the user
        user = User.objects.create(**validated_data)
        
        # Hash and set the password
        user.set_password(password)
        user.save()

        return user
    
 





class ActivityRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityRecord
        fields = '__all__'

