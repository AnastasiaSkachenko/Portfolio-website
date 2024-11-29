from rest_framework import status 
from rest_framework.response import Response
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Project
from rest_framework.decorators import api_view
from rest_framework import serializers

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'description', 'tools'] 


@api_view(['POST'])
def send_confirmation(request): 
    data = request.data
    name = data.get('name')
    email = data.get('email')
    body = data.get('body')

    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
 
    
    send_mail(
        'Thank you for your message!',
        f'Thank you for your message. I will review it as soon as I can.',
        'skachenkoa@gmail.com',
        [email],
        fail_silently=False,
    )

    send_mail(
        'New message',
        f'There is a new message on website. Name: {name}. Email: {email}. Message: {body}',
        'skachenkoa@gmail.com',
        ['nastaskacenko02@gmail.com'],
        fail_silently=False,
    )
    return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)
 
@api_view(['POST'])
def save_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Project saved."}, status=status.HTTP_200_OK)
    else:
        print(serializer.errors)
        return Response({"error": "Project not saved."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_project(request):
        projects = Project.objects.all()

        serializer = ProjectSerializer(projects, many=True)

        return JsonResponse({'projects': serializer.data}, status=status.HTTP_200_OK)