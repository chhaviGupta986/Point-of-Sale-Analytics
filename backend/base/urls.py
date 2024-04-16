from django.urls import path
from django.urls import re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns=[
    path('', views.loginuser, name='loginpage'),
    path('register', views.registeruser, name='registerpage'),
    path('logout/', views.logoutuser, name = 'logout'),
    path('home', views.home, name='home'),
    path('upload', views.uploadsheet, name='uploadsheet'),
]