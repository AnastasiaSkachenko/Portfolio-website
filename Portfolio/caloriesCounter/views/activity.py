from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from backend.authentication import customJWTAuthentication
from backend.models import ActivityRecord
from django.db.models import Prefetch
from backend.serializers import ActivityRecordSerializer 
from django.utils import timezone
from caloriesCounter.utils import recalculate_nutrition_for_today
from ..update_user_nutritions import update_daily_goals


class ActivityRecordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        activities = ActivityRecord.objects.filter(user=request.user)
        serialized_activities = ActivityRecordSerializer(activities, many=True).data
        
        return Response({"activities": serialized_activities}, status=status.HTTP_200_OK)


    def post(self, request):
        serializer = ActivityRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            update_daily_goals(request.user)

            return Response({"message": "Activity recorded successfully"})
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        activity = ActivityRecord.objects.get(id=request.data.get('id'))
        serializer = ActivityRecordSerializer(activity, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            update_daily_goals(request.user)

            return Response({"message": "Activity record updated successfully"})
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request): 
        id = request.query_params.get('id')
        activity = ActivityRecord.objects.get(id=id)
        activity.delete()

        update_daily_goals(request.user)

        return Response({'message': 'activity deleted successfully'}, status=status.HTTP_200_OK)


