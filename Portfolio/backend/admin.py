
from django.contrib import admin
from .models import Project, Skill

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'tools')  

@admin.register(Skill)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'experience')  
