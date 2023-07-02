from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index',),
    path('/new',views.new,name='newFormation'),
    path('/update',views.update,name='updateFormation'),
    path('/detaille<int:id>',views.detaille,name='detailleFormation'),
  #  path('attestation/',views.generate_attestation, name='generate_attestation'),

]