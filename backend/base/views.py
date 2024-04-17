from django.shortcuts import render,redirect
from .models import User, Links, Test, DemandForecasting
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
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import re
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
from .ML_product_demand_forecasting import forecast
# Create your views here.

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
    def scatter():
        x1 = [1,2,3,4]
        y1 = [30, 35, 25, 45]

        trace = go.Scatter(
            x=x1,
            y = y1
        )
        layout = dict(
            title='Simple Graph',
            xaxis=dict(range=[min(x1), max(x1)]),
            yaxis = dict(range=[min(y1), max(y1)])
        )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div


    context = {
        'users': users,
        'plot1': scatter()
    }
    return render(request, 'home.html', context)

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
    def scatter():
        x1 = [1,2,3,4]
        y1 = [30, 35, 25, 45]

        trace = go.Scatter(
            x=x1,
            y = y1
        )
        layout = dict(
            title='Simple Graph',
            xaxis=dict(range=[min(x1), max(x1)]),
            yaxis = dict(range=[min(y1), max(y1)])
        )

        fig = go.Figure(data=[trace], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    context ={
        'plot1': scatter()
    }

    return render(request, 'dash_template.html',context)

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
        companyname = request.user
        link = request.POST.get('link')

        if form.is_valid():
            link_instance = Links(companyname=companyname, link=link)
            link_instance.save()

            messages.success(request, "Link added successfully.")
            
            # data = form.cleaned_data
            # df = pd.DataFrame([data])
            # print(df)
            # rets=forecast(df)
            # order_of_return=['actuals','predictions','dates_to_plot','top_prod_indexes','r2_array']

            # demand_forecast = DemandForecasting(
            #     companyname=request.user,  # Assuming request.user is the company name
            #     actuals=rets['actuals'],
            #     predictions=rets['predictions'],
            #     dates=rets['dates_to_plot'],
            #     top_products=rets['top_prod_indexes'],
            #     rsquare=rets['r2_array']
            # )
            # demand_forecast.save()
    else:
        form = LinkForm()

    context = {
        'form': form
    }
    return render(request, 'uploadsheet.html', context)