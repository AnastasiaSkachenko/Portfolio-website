from django.urls import path 
from .views import SendConfirmationView, GetProjectView, GetSkillView

urlpatterns = [
    path('send-confirmation/', SendConfirmationView.as_view(), name='send_confirmation'), 
    path('get-project/', GetProjectView.as_view(), name='get_project'), 
    path('get-skill/', GetSkillView.as_view(), name='get_skill'),
]
