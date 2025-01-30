from rest_framework import serializers
from .models import Project, Skill, Product, Ingredient, Dish, DiaryRecord,  User



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
        fields = ['id', 'name', 'age', 'image', 'calories_d', 'protein_d', 'carbohydrate_d', 'fat_d', 'height', 'weight', 'activity_level']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)  # write_only ensures password isn't returned in the response

    class Meta:
        model = User
        fields = ['id', 'name', 'age', 'email', 'password', 'image', 'calories_d', 'protein_d', 'carbohydrate_d', 'fat_d', 'height', 'weight', 'activity_level']

    def create(self, validated_data):
        # Create the user object
        user = User.objects.create(
            name=validated_data.get('name', ''),
            age=validated_data.get('age', 18),
            image=validated_data.get('image', None),
            username=validated_data.get('email', '')
        )
        # Hash the password before saving the user
        user.set_password(validated_data['password'])
        user.save()  # Save the user to the database
        return user

    password = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User  # Use the related profile model if the user model has extended data
        fields = [
            'name', 'password', 'age', 'weight', 'height', 'calories_d', 
            'protein_d', 'carbohydrate_d', 'fat_d', 'activity_level', 'image'
        ]

    def create(self, validated_data):
        # Separate password from profile data
        password = validated_data.pop('password')
        
        # Create the user first
        user = User.objects.create(
            name=validated_data['name'],
        )
        
        # Hash and set the password
        user.set_password(password)
        user.save()

        # Now create the profile data for the user
        profile_data = {
            'user': user,
            'age': validated_data.get('age', 18),
            'weight': validated_data.get('weight', 0),
            'height': validated_data.get('height', 0),
            'calories_d': validated_data.get('calories_d', 0),
            'protein_d': validated_data.get('protein_d', 0),
            'carbohydrate_d': validated_data.get('carbohydrate_d', 0),
            'fat_d': validated_data.get('fat_d', 0),
            'activity_level': validated_data.get('activity_level', 1),
            'image': validated_data.get('image', None),
        }
        
        # Create and save the profile data
        user_profile = User.objects.create(**profile_data)

        return user_profile
    
