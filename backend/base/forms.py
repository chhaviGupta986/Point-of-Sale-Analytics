from django.forms import ModelForm, widgets
from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['company_name', 'email', 'type', 'years']