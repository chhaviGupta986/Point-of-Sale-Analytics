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
    REQUIRED_FIELDS = ['name', 'username'] 
    
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_permission_set')