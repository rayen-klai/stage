from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('/formation',include('formation.urls')),
    path('/user',include('user.urls')),
    path('',views.Monprofile,name='monprofil'),
]