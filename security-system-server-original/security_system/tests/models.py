from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class MyUser(AbstractUser):
    gender = models.IntegerField(null=True)
    contact = models.CharField(max_length=100)
    unit = models.CharField(max_length=200)
    authLevel = models.IntegerField(null=True)
    address = models.CharField(max_length=100)


admin.site.register(MyUser)
