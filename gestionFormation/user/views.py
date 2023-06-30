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

def index(request):
    return render(request,'admin/user/index.html',{'users' : Profile.objects.all })

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
            if str(user2.id) in participants.keys() and participants[str(user2.id)] == 1:
                matching_formations.append(form)


    if request.method == 'POST' and 'supprimer' in request.POST:
        user2.delete()
        return render(request,'admin/user/index.html',{'users' : Profile.objects.all })
    


    if request.method == 'POST' and 'modifier' in request.POST:
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        cin = request.POST.get('cin')
        org = request.POST.get('org')

        if not email or not pwd or not nom or not prenom or not cin or not org:
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
        file = request.FILES.get('file')
        
        if file:
            file_path = default_storage.save(file.name, file)
            user2.img = file_path

        if pwd!='password':
            user2.set_password(pwd)
        user2.save()
    return render(request,'admin/user/profile.html',{'user2' : user2 , 'formations' : matching_formations})



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