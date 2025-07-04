from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.authentication import customJWTAuthentication
from backend.models import ActivityRecord
from django.db.models import Prefetch
from backend.serializers import ActivityRecordSerializer 
from django.utils.timezone import  datetime
from ..update_user_nutritions import update_daily_goals
from django.utils.dateparse import parse_datetime 



class GetAllActivities(APIView): 
    permission_classes = []

    def get(self, request):
        try:
            activities = ActivityRecord.objects.filter(is_deleted=False).order_by('-timestamp')
            activities_data = ActivityRecordSerializer(activities, many=True).data


            return Response({"activities":activities_data}, status=200)
        except:
            return Response({"error": 'Failed to fetch activities'}, status=status.HTTP_400_BAD_REQUEST)



class GetUpdatedActivities(APIView):
    permission_classes = []  

    def get(self, request):
        last_synced = request.query_params.get('last_synced')
        if not last_synced:
            return Response({"error": "last_synced query param is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # parse the string datetime to Python datetime object
        last_synced_dt = parse_datetime(last_synced)
        if not last_synced_dt:
            return Response({"error": "Invalid datetime format for last_synced"}, status=status.HTTP_400_BAD_REQUEST)

        activities = ActivityRecord.objects.filter(last_updated__gt=last_synced_dt)
        deleted_activities = list(ActivityRecord.objects.filter(is_deleted=True).values_list('id', flat=True))

        serializer = ActivityRecordSerializer(activities, many=True)
        return Response({"activities": serializer.data, "deleted_activities": deleted_activities}, status=status.HTTP_200_OK)



class ActivityRecordView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = ActivityRecord.objects.filter(user=request.user)
        serialized_activities = ActivityRecordSerializer(activities, many=True).data
        
        return Response({"activities": serialized_activities}, status=status.HTTP_200_OK)


    def post(self, request):
        print(request.data)
        serializer = ActivityRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            activity = ActivityRecord.objects.get(id=request.data.get('id'))


            timestamp = datetime.fromisoformat(request.data.get('timestamp'))
            update_daily_goals(request.user, timestamp)

            return Response({"message": "Activity recorded successfully", "calories_burned":activity.calories_burned})
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        activity = ActivityRecord.objects.get(id=request.data.get('id'))
        previous_timestamp = activity.timestamp
        serializer = ActivityRecordSerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            activity = ActivityRecord.objects.get(id=request.data.get('id'))


            timestamp = datetime.fromisoformat(request.data.get('timestamp'))
            update_daily_goals(request.user, timestamp, previous_timestamp)

            return Response({"message": "Activity record updated successfully", "calories_burned":activity.calories_burned})
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request): 
        id = request.query_params.get('id')
        activity = ActivityRecord.objects.get(id=id)
        timestamp = activity.timestamp
        activity.delete()

        update_daily_goals(request.user, timestamp)

        return Response({'message': 'activity deleted successfully'}, status=status.HTTP_200_OK)


