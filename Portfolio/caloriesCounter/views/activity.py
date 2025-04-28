from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.authentication import customJWTAuthentication
from backend.models import ActivityRecord, Exercise, WorkoutTemplate, WorkoutExercise, TabataTemplate
from caloriesCounter.utils import calculate_custom_workout_calories, calculate_tabata_duration
from django.db.models import Prefetch

from backend.serializers import (
    CreateTabataActivitySerializer,
    CreateWorkoutTemplateActivitySerializer,
    CreateCardioActivitySerializer,
    ActivityRecordSerializer, 
    WorkoutTemplateSerializer, 
    WorkoutExerciseSerializer,
    ExerciseSerializer, 
    TabataTemplateSerializer
)



class ActivityRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = ActivityRecord.objects.filter(user=request.user)
        serialized_activities = []

        for activity in activities:
            data = ActivityRecordSerializer(activity).data

            if activity.activity_type == "workout" and activity.related_id:
                try:
                    workout = WorkoutTemplate.objects.get(id=activity.related_id)
                    # Serialize the workout or include desired fields
                    data["workout"] = {
                        "id": workout.id,
                        "name": workout.name,
                        # Add other relevant fields
                    }
                except WorkoutTemplate.DoesNotExist:
                    data["workout"] = None  # Or handle gracefully

            if activity.activity_type == "tabata" and activity.related_id:
                try:
                    workout = TabataTemplate.objects.get(id=activity.related_id)
                    # Serialize the workout or include desired fields
                    data["tabata"] = {
                        "id": workout.id,
                        "name": workout.name,
                        # Add other relevant fields
                    }
                except WorkoutTemplate.DoesNotExist:
                    data["tabata"] = None  # Or handle gracefully



            serialized_activities.append(data)
        
        return Response({"activities": serialized_activities}, status=status.HTTP_200_OK)


    def post(self, request):
        activity_type = request.data.get('activity_type')
        print(activity_type, 'activity time')
        print(request.data)
        if not activity_type:
            print('no activity type')
            return Response({"error": "activity_type is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer_class_map = {
            'tabata': CreateTabataActivitySerializer,
            'workout': CreateWorkoutTemplateActivitySerializer,
            'run': CreateCardioActivitySerializer,
            'walk_time': CreateCardioActivitySerializer,
            'walk_steps': CreateCardioActivitySerializer,
            'interval_run': CreateCardioActivitySerializer,
        }

        serializer_class = serializer_class_map.get(activity_type)
        if not serializer_class:
            print('no  serializer')
            return Response({"error": f"Unsupported activity_type: {activity_type}"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            result = serializer.save()
            return Response({"message": "Activity recorded successfully", "data": result})
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): 
        id = request.query_params.get('id')
        activity = ActivityRecord.objects.get(id=id)
        activity.delete()
        return Response({'message': 'activity deleted successfully'}, status=status.HTTP_200_OK)


class ExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        exercises = Exercise.objects.all()
        serializer = ExerciseSerializer(exercises, many=True)
        return Response({'exercises': serializer.data}, status=status.HTTP_200_OK)
    
         
class WorkoutExerciseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print('workout exercise', request.data)

        serializer = WorkoutExerciseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.data.get('calculate'):
                workout = WorkoutTemplate.objects.get(id=request.data.get('workout'))
                exercises = WorkoutExercise.objects.filter(workout=request.data.get('workout'))
                if workout:
                    workout.total_calories = calculate_custom_workout_calories(exercises, request.user.weight)
                    workout.save()
            return Response( status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        id = request.query_params.get('id')

        try:
            workout_exercise = WorkoutExercise.objects.get(id=id)
        except WorkoutExercise.DoesNotExist:
            return Response({"error": "Workout exercise not found"}, status=status.HTTP_404_NOT_FOUND)


        serializer = WorkoutExerciseSerializer(workout_exercise, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Workout exercise updated successfully"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): 
        id = request.query_params.get('id')
        print(id, request.query_params)
        workout_exercise = WorkoutExercise.objects.get(id=id)
        workout_exercise.delete()
        return Response({'message': 'workout exercise deleted successfully'}, status=status.HTTP_200_OK)



class WorkoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workouts = WorkoutTemplate.objects.prefetch_related(
            Prefetch('exercises', queryset=Exercise.objects.all(), to_attr='prefetched_exercises')
        )
        serializer = WorkoutTemplateSerializer(workouts, many=True)
        return Response({"workouts": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = WorkoutTemplateSerializer(data=request.data)
        if serializer.is_valid():
            workout = serializer.save()
            return Response( {'id': workout.id}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        workout_id = request.query_params.get('id')

        try:
            workout = WorkoutTemplate.objects.get(id=workout_id)
        except WorkoutTemplate.DoesNotExist:
            return Response({"error": "Workout not found"}, status=status.HTTP_404_NOT_FOUND)


        serializer = WorkoutTemplateSerializer(workout, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Workout updated successfully"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request): 
        id = request.query_params.get('id')
        workout = WorkoutTemplate.objects.get(id=id)
        workout.delete()
        return Response({'message': 'workout deleted successfully'}, status=status.HTTP_200_OK)







class GetWorkoutById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id = request.query_params.get('id')
        workout = WorkoutTemplate.objects.get(id=id)
        serializer = WorkoutTemplateSerializer(workout)
        return Response({"workout": serializer.data}, status=status.HTTP_200_OK)





class TabataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tabatas = TabataTemplate.objects.all()
        serializer = TabataTemplateSerializer(tabatas, many=True)
        return Response({"tabatas": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data, 'data')
        serializer = TabataTemplateSerializer(data=request.data.get('tabata'))
        if serializer.is_valid():
            tabata = serializer.save()
            if 'exercises' in request.data:
                tabata.exercises.set(request.data['exercises'])
                tabata.duration = calculate_tabata_duration(tabata)
                tabata.save()

            return Response( {'id': tabata.id}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
