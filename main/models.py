from django.db import models

class Task(models.Model):
    created_time = models.DateTimeField()
    date_time = models.CharField(max_length=100,blank=True)
    status = models.IntegerField()
    success = models.IntegerField()
# Create your models here.
