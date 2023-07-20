from datetime import date
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Profile 
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.auth import logout
from formation.models import formation
# Create your views here.
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import cv2
import os
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .serializers import ProfileSerializer

def custom_login_required(function=None):
    login_url = '/signup'  # Specify your custom login URL
    redirect_field_name = ''  # Specify your custom redirect field name

    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)


@custom_login_required
@staff_member_required
def index(request,x):
    print(x)
    if (x=='0'):
        print('a')
        return render(request,'admin/user/index.html',{'users' : Profile.objects.all() })
    else:
        users = Profile.objects.filter(role=x)
        return render(request, 'admin/user/index.html', {'users': users})
    
@custom_login_required
@staff_member_required
def profile(request,id):
    user2 = Profile.objects.get(id=id)    
    formations_list = formation.objects.all()
    matching_formations = []
    for form in formations_list:
        if(user2.role == 'Formateur'):
            if form.formateur == user2:
                matching_formations.append(form)
        else:
            participants = form.participants
            if str(user2.id) in participants.keys() and participants[str(user2.id)] != 0:
                matching_formations.append(form)


    if request.method == 'POST' and 'supprimer' in request.POST:
        for fm in matching_formations:
            if(user2.role == 'Formateur'):
                fm.formateur = None 
            else:
                del fm.participants[str(id)]
            fm.save()
        user2.delete()
        return render(request,'admin/user/index.html',{'users' : Profile.objects.all })
    
    if request.method == 'POST' and 'btn_ats' in request.POST:
        f = formation.objects.get(id=request.POST.get('btn_ats'))
        template = cv2.imread("staticfiles/attestation_template.png")
        nom_pre = f"{user2.last_name} {user2.first_name}"
        frm = f"{f.titre}"
        forma = f"{f.formateur.last_name} {f.formateur.first_name}"
        today =date.today().strftime("%Y-%m-%d")
        font_scale = 2  # Adjust the font scale value as per your requirement
        thickness = 2  # Adjust the thickness of the text
        cv2.putText(template, nom_pre, (800, 750), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness, cv2.LINE_AA)
        cv2.putText(template,frm, (770, 950), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), thickness, cv2.LINE_AA)
        cv2.putText(template,forma, (870, 1215), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), thickness, cv2.LINE_AA)
        cv2.putText(template,today, (910, 1290), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), thickness, cv2.LINE_AA)
        
        if not os.path.exists('staticfiles/attestation/'+ frm):
            os.makedirs('staticfiles/attestation/'+ frm)
        
        path = 'staticfiles/attestation/'+ frm +f'/{user2.first_name}{user2.last_name}.jpg'
        cv2.imwrite(path,template)

    if request.method == 'POST' and 'modifier' in request.POST:
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        cin = request.POST.get('cin')
        org = request.POST.get('org')
        role = request.POST.get('role')
        if not email or not nom or not prenom or not cin or not org:
            messages.error(request, "Veuillez remplir tous les champs !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cin_regex = RegexValidator(regex=r'^\d{8}$', message="CIN invalide.")
        try:
            cin_regex(cin)
        except ValidationError as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        user2.first_name = nom 
        user2.last_name = prenom 
        user2.cin = cin 
        user2.org = org
        user2.email = email 
        user2.role = role 

        file = request.FILES.get('file')
        
        if file:
            file_path = default_storage.save(file.name, file)
            user2.img = file_path
        user2.save()
    return render(request,'admin/user/profile.html',{'user2' : user2 , 'formations' : matching_formations})



@custom_login_required
@staff_member_required
def addFormateur(request):
    if request.method == 'POST':    
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        cin = request.POST.get('cin')
        org = request.POST.get('org')
        
        if not email or not nom or not prenom or not cin or not org:
            messages.error(request, "Veuillez remplir tous les champs !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cin_regex = RegexValidator(regex=r'^\d{8}$', message="CIN must be an 8-digit number.")
        try:
            cin_regex(cin)
        except ValidationError as e:
            messages.error(request, str(e))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        
        user = Profile(email=email, first_name=nom, last_name=prenom, cin=cin, organisme=org, role='Formateur',)
      
        user.save()
        return render(request, 'admin/user/index.html', {'users': Profile.objects.all()})

    return render(request,'admin/user/newFormateur.html')

def logoutf(request):
    logout(request)
    return redirect('admin')

