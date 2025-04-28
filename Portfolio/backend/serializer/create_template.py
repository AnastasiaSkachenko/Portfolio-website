from backend.models import   TabataTemplate, WorkoutExercise
from rest_framework import serializers



class WorkoutTemplateExerciseInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise', 'reps', 'time_minutes', 'weight_group']


class CreateTabataTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TabataTemplate
        fields = ['name', 'rounds', 'work_seconds']

