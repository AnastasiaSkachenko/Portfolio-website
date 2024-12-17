from django.urls import path 
from .views import send_confirmation, get_skill, get_project

urlpatterns = [
    path('send-confirmation/', send_confirmation, name='send_confirmation'), 
    path('get-project/', get_project, name='get_project'), 
    path('get-skill/', get_skill, name='get_skill')
]
