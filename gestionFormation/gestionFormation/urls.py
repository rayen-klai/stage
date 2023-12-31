"""
URL configuration for gestionFormation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import path,include
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from customadmin import views as v2

urlpatterns = [
    path('auth/', include('dj_rest_auth.urls')),
    path('dj-admin',admin.site.urls),
    path('admin',include('customadmin.urls')),
    path('',views.acc,name='acc'),
    path('formation',views.nosformations,name='nosformations'),
    path('formateur',views.nosformateurs,name='nosformateurs'),
    path("espaceformateur", views.cal, name="calendar"),
    path("espaceformateur/presence/<int:id>/<str:date2>", views.presence, name="presence"),
    path('signup',v2.admin_login,name='admin_login'),
    path('acc', views.logoutf, name='logoutt'),
    path('profile', views.profile, name='profile'),
    path('mesparticipations', views.part, name='part'),
    path('mesparticipations/evaluation/<id>', views.evaluation, name='evaluation'),
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name="front/reset.html"),name="reset_password"),
    path('reset_password_sent/',auth_views.PasswordResetDoneView.as_view(template_name="front/resetdone.html"),name="password_reset_done"),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="front/resetpwd.html"),name="password_reset_confirm"),
    path('reset_password_complete/',auth_views.PasswordResetCompleteView.as_view(template_name="front/resetcomplete.html"),name="password_reset_complete"),
    path('all_events/', views.all_events, name='all_events'),
    path('api',views.getRoutes),
    path('api/endpoint',views.pres),
    path('save-character',views.save_character,name="save-character")
]

urlpatterns +=  static(settings.MEDIA_URL,document_root= settings.MEDIA_ROOT)
