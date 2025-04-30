from rest_framework import serializers
from .models import (Project, Skill, Product, Ingredient, Dish, DiaryRecord,  WorkoutTemplate, WorkoutExercise,
                    User, ActivityRecord, WorkoutTemplate,TabataTemplate, Exercise)
    
from django.contrib.auth.hashers import make_password
from caloriesCounter.utils import (
    calculate_custom_workout_calories, calculate_tabata_calories,
    calculate_steps_calories, calculate_run_walk_calories, calculate_calories_from_met
)


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


class ExerciseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exercise
        fields =  '__all__'



class ExerciseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name']

class WorkoutExerciseSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source='exercise.name', read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(),
        source='exercise',
    )


    class Meta:
        model = WorkoutExercise
        fields = ['id', 'exercise_name', 'reps', 'sets', 'time_minutes', 'weight_group', 'exercise_id', 'workout']


class WorkoutTemplateSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField()
    class Meta:
        model = WorkoutTemplate
        fields = ['id', 'name', 'total_calories', 'exercises']

    def get_exercises(self, obj):
        # Manually fetch the related exercises with the desired fields
        workout_exercises = WorkoutExercise.objects.filter(workout=obj)
        exercises_data = []
        
        for workout_exercise in workout_exercises:
            exercise_data = {
                'id': workout_exercise.id,
                'exercise_name': workout_exercise.exercise.name,
                'reps': workout_exercise.reps,
                'sets': workout_exercise.sets,
                'time_minutes': workout_exercise.time_minutes,
                'weight_group': workout_exercise.weight_group,
                'exercise_id': workout_exercise.exercise.id,
            }
            exercises_data.append(exercise_data)
        
        return exercises_data


class GETTabataTemplateSerializer(serializers.ModelSerializer):
    exercises = ExerciseSimpleSerializer(many=True)

    class Meta:
        model = TabataTemplate
        fields = ['id', 'name', 'exercises', 'rounds', 'work_seconds', 'rest_seconds', 'duration']



class TabataTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = TabataTemplate
        fields = '__all__'



class CreateTabataActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context['request'].user
        tabata = TabataTemplate.objects.get(id=validated_data['id'])
        exercises = tabata.exercises.all()
        calories = calculate_tabata_calories(exercises, user.weight,
                                            tabata.rounds, tabata.work_seconds)

        ActivityRecord.objects.create(
            user=user,
            activity_type='tabata',
            related_id=tabata.id,
            weight_kg=user.weight,
            calories_burned=calories
        )
        return {"tabata": tabata.name, "calories": calories}


class CreateWorkoutTemplateActivitySerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        user = self.context['request'].user
        template = WorkoutTemplate.objects.get(id=validated_data['id'])
        exercises = template.workoutexercise_set.all()
        calories, total_time = calculate_custom_workout_calories(exercises, user.weight)

        activity = ActivityRecord.objects.create(
            user=user,
            activity_type='workout',
            duration_minutes=total_time,
            weight_kg=user.weight,
            calories_burned=calories,
            related_id=template.id
        )



 
        return {"template": template.name, "calories": calories}


class CreateCardioActivitySerializer(serializers.Serializer):
    activity_type = serializers.ChoiceField(choices=[
        ('run', 'Run'),
        ('walk_time', 'Walk (Time)'),
        ('walk_steps', 'Walk (Steps)'),
        ('interval_run', 'Interval Run'),
    ])
    duration_minutes = serializers.FloatField(required=False)
    steps = serializers.IntegerField(required=False)
    distance_km = serializers.FloatField(required=False)
    weight_kg = serializers.FloatField()

    def validate(self, data):
        atype = data['activity_type']
        if atype == 'walk_steps' and 'steps' not in data:
            raise serializers.ValidationError("Steps required for walk_steps")
        if atype != 'walk_steps' and 'duration_minutes' not in data:
            raise serializers.ValidationError("Duration required")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        weight_kg = user.weight
        calories = 0
        activity_type = validated_data['activity_type']

        if activity_type == 'walk_steps':
            calories = calculate_steps_calories(validated_data['steps'], weight_kg)
        else:
            # MET values based on standard estimates
            MET_VALUES = {
                'walk_time': 3.5,
                'run': 9.3,
                'interval_run': 10.5
            }
            met = MET_VALUES[activity_type]
            calories = calculate_run_walk_calories(9.8, weight_kg, validated_data['duration_minutes'], validated_data['distance_km'], activity_type)

        activity = ActivityRecord.objects.create(
            user=user,
            activity_type=validated_data['activity_type'],
            duration_minutes=validated_data.get('duration_minutes'),
            steps=validated_data.get('steps'),
            distance_km=validated_data.get('distance_km'),
            weight_kg=weight_kg,
            calories_burned=calories
        )

        return {"activity": activity.activity_type, "calories": calories}
