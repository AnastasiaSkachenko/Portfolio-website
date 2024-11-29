from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=180)
    description = models.TextField()
    tools = models.TextField()
