from django.urls import path
from django.urls import re_path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns=[
    path('', views.registeruser, name='registerpage'),
    path('home', views.home, name='home'),
]