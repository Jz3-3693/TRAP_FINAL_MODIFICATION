from django.db import models
# class trap(models.Model):
 
#  place = models.CharField(max_length=255)
#  weather =models.CharField(max_length=255) 
#  time = models.DateTimeField()
 
class contact(models.Model):
 name = models.CharField(max_length=255)
 email = models.CharField(max_length=255)
 message =models.CharField(max_length=255)
 # Create your models here.
 
from django.db import models
from django.contrib.auth.models import User  # Import Django's built-in User model

class AccidentPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link each prediction to a user
    latitude = models.FloatField()
    longitude = models.FloatField()
    cluster = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto-generated timestamp

    def __str__(self):
        return f"User {self.user.username} - Cluster {self.cluster} at ({self.longitude}, {self.latitude})"
