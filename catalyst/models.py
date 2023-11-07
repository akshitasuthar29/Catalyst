from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Catalyst(models.Model):
    name  = models.TextField()
    domain = models.TextField()
    year = models.DecimalField(decimal_places=2,max_digits=50)
    industry = models.TextField()
    size_range = models.TextField()
    city = models.TextField()
    country = models.TextField()
    linkedin_url = models.TextField()


class CMIUsers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    


