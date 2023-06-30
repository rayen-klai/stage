from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='indexUser'),
    path('/profile<int:id>',views.profile,name='profilUser'),
    path('/newFormateur',views.addFormateur,name='newFormatuer'),
]