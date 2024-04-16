from django.shortcuts import render,redirect
from .models import User, Links
from .forms import MyUserCreationForm, LoginForm, LinkForm
from django.db.models import Q
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from urllib.parse import unquote
from django.contrib.auth.hashers import check_password

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
                login(request, user)
                return redirect('home')
    context = {'form': form}
    return render(request, 'register.html', context)

def loginuser(request):
    page = 'login'
    form = LoginForm()

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return render(request, 'login.html', {'page': page, 'form': form})

        # Check if password is correct
        if check_password(password, user.password):
            
            if user.is_superuser:
                login(request, user)
                messages.success(request, 'Login Successful, Welcome Admin!')
                return redirect('home')
            else:
                login(request, user)
                messages.success(request, 'Login Successful!')
                return redirect('home')
            
        else:
            messages.error(request, 'Incorrect Password.')

    context = {
        'page': page,
        'form': form
    }

    return render(request, 'login.html', context)


def logoutuser(request):
    logout(request)
    messages.success(request, 'Successfully Logged Out.')
    return redirect('home')

def home(request):
    return render(request, 'home.html')

def uploadsheet(request):
    form = LinkForm()
    
    if request.method == "POST":
        # Retrieve company name from POST data
        company_id = request.POST.get('companyname')
        link = request.POST.get('link')

        # Fetch the User instance using the provided company ID
        company = User.objects.get(pk=company_id)

        # Print company name for debugging
        print(company.company_name)

        # Create form instance with the fetched User instance
        form = LinkForm(request.POST, initial={'companyname': company})

        if form.is_valid():
            form.save()
            messages.success(request, "Link added successfully.")

    context = {
        'form': form
    }

    return render(request, 'uploadsheet.html', context)
