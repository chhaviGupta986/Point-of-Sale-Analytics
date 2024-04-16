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
from django.contrib.auth.hashers import make_password
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from oauth2client.file import Storage
from .visualization import hello
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

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

        #checks whether user exists
        try:
            email = User.objects.get(email = email)
        except:
            messages.error(request, 'User does not exist.')

        #checks for the user with given mail and password
        user = authenticate(request, email = email, password = password)
    
        # Check if password is correct
        if user != None:
            
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

@login_required(login_url = 'loginpage')
def home(request):
    users = User.objects.all()
    context = {
        'users': users
    }
    return render(request, 'home.html', context)

@login_required(login_url = 'loginpage')
def uploadsheet(request):
    form = LinkForm()
    
    if request.method == "POST":
        # Retrieve company name from POST data
        company_id = request.POST.get('companyname')
        link = request.POST.get('link')

        sheetDF = pd.read_html(link)[0]
        print(sheetDF)

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

@login_required(login_url = 'loginpage')
def profile(request, pk):
    user = User.objects.get(id=pk)
    context={
        'user':user
    }
    return render(request, 'profile.html', context)

@login_required(login_url = 'loginpage')
def visualization(request, pk): 
    return render(request, 'visualization.html')

@login_required(login_url='loginpage')
def prediction(request, pk):
    data = hello()
    data = hello()
    return render(request, 'predictions.html')

@login_required(login_url = 'loginpage')
def googleauthenticate():
    flow = InstalledAppFlow.from_client_secrets_file(
        '../client_secret_new2.json', 
        ['https://www.googleapis.com/auth/spreadsheets.readonly'], 
        redirect_uri='http://localhost:8000')
    credentials = flow.run_local_server(port=8000)
    return credentials

@login_required(login_url = 'loginpage')
def get_spreadsheet_id_from_url(url):
    try:
        parts = url.split('/')
        spreadsheet_id = parts[-2]
        return spreadsheet_id
    except Exception as e:
        # Handle any errors that occur during ID extraction
        print("Error extracting Spreadsheet ID:", e)
        return None

@login_required(login_url = 'loginpage')
def uploadsheet(request):
    if request.method == "POST":
        form = LinkForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, "Link added successfully.")
            
            # Get the data from the form
            data = form.cleaned_data
            print(data)
            # Create a pandas DataFrame from the data
            df = pd.DataFrame([data])
            
            # Print the DataFrame
            print(df)
    else:
        form = LinkForm()

    context = {
        'form': form
    }
    return render(request, 'uploadsheet.html', context)