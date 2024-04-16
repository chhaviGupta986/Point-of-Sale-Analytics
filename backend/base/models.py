from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import os
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import shutil

class User(AbstractUser):
    company_name = models.CharField(max_length = 200, null = True)
    email = models.EmailField(unique = True, null = True)
    type = models.CharField(max_length = 200, null = True)
    years = models.BigIntegerField(null = True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name', 'username']

class Links(models.Model):
    companyname = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    link = models.CharField(max_length=300)
    
    def __str__(self):
        return self.link