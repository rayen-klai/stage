from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index',),
    path('/new',views.new,name='newFormation'),
    path('/update',views.update,name='updateFormation'),
    path('/detaille<int:id>',views.detaille,name='detailleFormation'),
    path('/presence/<int:id>/<str:date2>', views.presence2 , name='presence2'),
    path('pdf_view/<int:id>', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download', views.DownloadPDF.as_view(), name="pdf_download"),
  #  path('attestation/',views.generate_attestation, name='generate_attestation'),

]