from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=180)
    description = models.TextField()
    tools = models.TextField()

class Skill(models.Model):
    name = models.CharField(max_length=180)
    image = models.CharField(max_length=180)
    experience = models.IntegerField()
