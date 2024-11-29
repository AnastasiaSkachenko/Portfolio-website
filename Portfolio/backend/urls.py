from django.urls import path 
from .views import send_confirmation, save_project, get_project

urlpatterns = [
    path('send-confirmation/', send_confirmation, name='send_confirmation'), 
    path('save-project/', save_project, name='save'), 
    path('get-project/', get_project, name='get'), 
]
