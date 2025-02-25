from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Project, Skill
from .serializers import ProjectSerializer, SkillSerializer
from rest_framework.permissions import AllowAny

# --- 📩 Send Confirmation Email ---
class SendConfirmationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name')
        email = data.get('email')
        body = data.get('body')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        send_mail(
            'Thank you for your message!',
            'Thank you for your message. I will review it as soon as I can.',
            'skachenkoa@gmail.com',
            [email],
            fail_silently=False,
        )

        send_mail(
            'New message',
            f'There is a new message on the website. Name: {name}. Email: {email}. Message: {body}',
            'skachenkoa@gmail.com',
            ['nastaskacenko02@gmail.com'],
            fail_silently=False,
        )

        return Response({"message": "Verification code sent."}, status=status.HTTP_200_OK)


# --- 💾 Save Project ---
class SaveProjectView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project saved."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Project not saved."}, status=status.HTTP_400_BAD_REQUEST)


# --- 📌 Get Projects ---
class GetProjectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return JsonResponse({'projects': serializer.data}, status=status.HTTP_200_OK)


# --- 📌 Get Skills ---
class GetSkillView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return JsonResponse({'skills': serializer.data}, status=status.HTTP_200_OK)
