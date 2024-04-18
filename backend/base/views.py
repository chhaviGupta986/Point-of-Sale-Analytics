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
from django.shortcuts import get_object_or_404
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import re
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objects as go
import json
from .ML_product_demand_forecasting import forecast
from .ML_inventory_analysis import generate_ABC_data
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

    context = {
        'users': users,
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
    demand_forecast = get_object_or_404(DemandForecasting, companyname=request.user)
    actuals = demand_forecast.actuals
    predictions = demand_forecast.predictions
    dates = demand_forecast.dates
    error = demand_forecast.rsquare

    data_list = json.loads(actuals)
    predicted_list = json.loads(predictions)
    array = dates.split(', ')

    # Define scatter function before the loop
    def scatter(value, arr, arr2):
        x1 = [1, 2, 3, 4, 5, 6, 7]
        y1 = arr
        y2 = arr2

        trace1 = go.Scatter(
            x=x1,
            y=y1,
            name='Actual',
            mode='lines+markers',
            line=dict(color='blue', dash='solid'),
            marker=dict(color='blue', size=8)
        )

        trace2 = go.Scatter(
            x=x1,
            y=y2,
            name='Predicted',
            mode='lines+markers',
            line=dict(color='red', dash='dash'),
            marker=dict(color='red', size=8)
        )

        layout = dict(
            title=f'Product ID: {k}',
            plot_bgcolor='lightgrey',
            paper_bgcolor='#172A46',
            xaxis=dict(range=[min(x1), max(x1)]),
            yaxis=dict(range=[0, max(max(y1), max(y2))]),
            font=dict(family='Arial', size=12, color='white'),
        )

        fig = go.Figure(data=[trace1, trace2], layout=layout)
        plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        return plot_div

    plots = []
    k = 1  # Initialize k before the loop
    # Call scatter function inside the loop and collect the plot_divs
    for arr, arr2 in zip(data_list, predicted_list):
        plot_div = scatter(7, arr, arr2)
        plots.append(plot_div)
        k += 1  # Increment k for each plot

    context = {
        'plots': plots
    }

    return render(request, 'predictions.html', context)


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
            
            df = form.cleaned_data['link_data']
            df_copy=df.copy()

            rets=forecast(df)

            demand_forecast = DemandForecasting(
                companyname=request.user,
                actuals=rets[0],
                predictions=rets[1],
                dates=rets[2],
                top_products=rets[3],
                rsquare=rets[4]
            )
            demand_forecast.save()
            
            rets2=generate_ABC_data(df_copy)
            
    else:
        form = LinkForm()

    context = {
        'form': form
    }
    return render(request, 'uploadsheet.html', context)