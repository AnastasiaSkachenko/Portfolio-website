from rest_framework.response import Response
from backend.models import  DiaryRecord, DailyGoals
from backend.serializers import  DiarySerializer, DailyGoalSerializer
from rest_framework.views import APIView
from rest_framework import  status 
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from backend.authentication import customJWTAuthentication
from django.utils.dateparse import parse_datetime


class GetAllDiaryRecords(APIView):
    permission_classes = []

    def get(self, request):
        try:
            records = DiaryRecord.objects.filter(is_deleted=False).order_by('-id')
            records_data = DiarySerializer(records, many=True).data
            return Response({"diary_records": records_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Failed to fetch diary records"}, status=status.HTTP_400_BAD_REQUEST)


class GetUpdatedDiaryRecords(APIView):
    permission_classes = []

    def get(self, request):
        last_synced = request.query_params.get('last_synced')
        if not last_synced:
            return Response({"error": "last_synced query param is required"}, status=status.HTTP_400_BAD_REQUEST)

        last_synced_dt = parse_datetime(last_synced)
        if not last_synced_dt:
            return Response({"error": "Invalid datetime format for last_synced"}, status=status.HTTP_400_BAD_REQUEST)

        # Updated and deleted diary records
        updated_records = DiaryRecord.objects.filter(last_updated__gt=last_synced_dt)
        deleted_record_ids = list(
            DiaryRecord.objects.filter(is_deleted=True).values_list('id', flat=True)
        )

        serializer = DiarySerializer(updated_records, many=True)
        return Response({
            "diary_records": serializer.data,
            "deleted_records": deleted_record_ids
        }, status=status.HTTP_200_OK)




class DailyGoalView(APIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]

    def get(self, request):  
        records = DailyGoals.objects.filter(user=request.user.id) # Get all records from the table
        serializer = DailyGoalSerializer(records, many=True)  # Serialize multiple records
        return Response({'goals':serializer.data}, status=status.HTTP_200_OK)


class DiaryView(APIView): 
    permission_classes = [IsAuthenticated]
    authentication_classes = [customJWTAuthentication]

    def get(self, request):  
        records = DiaryRecord.objects.filter(user=request.user.id) # Get all records from the table
        serializer = DiarySerializer(records, many=True)  # Serialize multiple records
        return Response({'diaryRecords':serializer.data}, status=status.HTTP_200_OK)
 
    def post(self, request):
        data = request.data.copy()  
        print(data, 'data \n\n\n\n\n\n')
        data['date'] = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M')
      
        serializer = DiarySerializer(data=data)
         
        if serializer.is_valid(): 
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        record_id = request.query_params.get('id')
        try:
            record = DiaryRecord.objects.get(id=record_id)
        except DiaryRecord.DoesNotExist:
            return Response({"error": "Dish not found"}, status=status.HTTP_404_NOT_FOUND)

        print(request.data, 'request data')
        serializer = DiarySerializer(record, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Record updated successfully", "record": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request):  
        id = request.query_params.get('id')

        record = DiaryRecord.objects.get(id=id)
 
        record.delete()

        return Response({"message": "Dish record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


