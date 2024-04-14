from django.shortcuts import render,redirect
from .models import User
from .forms import MyUserCreationForm
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote

def registeruser(request):
    form = MyUserCreationForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data['email']

            # Check if a user with the provided email already exists
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                if not existing_user.is_verified:
                    messages.error(request, 'You already have an account.')

            else:
                user.save()
                return redirect('home')
    context = {'form': form}
    return render(request, 'Home.tsx', context)

def home(request):
    return render(request, 'home.html')