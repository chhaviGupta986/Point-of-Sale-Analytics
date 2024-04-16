from django.forms import ModelForm, widgets
from django import forms
from .models import User, Links
from django.contrib.auth.forms import UserCreationForm

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['company_name', 'email', 'username', 'type', 'years']
        
class LoginForm(ModelForm):
    class Meta:
        model = User
        fields = ['email','password']

class LinkForm(ModelForm):
    class Meta:
        model = Links
        fields = ['companyname', 'link']