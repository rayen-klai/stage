from django.shortcuts import redirect, render
from django.http import HttpResponse 
from django.contrib.auth import logout
# Create your views here.
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.core.files.storage import default_storage
from formation.models import formation

def acc(request):
    return render(request,'accueill.html')

def nosformations(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            if 'fr_par' in request.POST:
                id = request.POST.get('fr_par')
                formation_instance = formation.objects.get(id=id)
                formation_instance.participants[request.user.id] = 0  
                formation_instance.save()
            elif 'fr_att' in request.POST:
                id = request.POST.get('fr_att')
                formation_instance = formation.objects.get(id=id)
                formation_instance.participants.pop(str(request.user.id), None)

                formation_instance.save()
        else:
            return redirect('admin_login')

    return render(request, 'front/nosFormations.html', {'formations': formation.objects.all()})

def nosformateurs(request):
    return render(request,'front/nosFormateurs.html')

def signup(request):
    return render(request,'front/signup.html')

def logoutf(request):
    logout(request)
    return redirect('acc')

def profile(request):
    user = request.user
    print(user)
    if request.method == 'POST':
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
        user.first_name = nom 
        user.last_name = prenom 
        user.cin = cin 
        user.organisme = org
        user.email = email 
        file = request.FILES.get('file')
        
        if file:
            file_path = default_storage.save(file.name, file)
            user.img = file_path

        if pwd!='password':
            user.set_password(pwd)
        
        user.save()
         
    context = {
        'user': user,
        'messages': messages.get_messages(request)
    }
    return render(request, 'front/form.html', context)

def part(request):
    return render(request,'front/mesParticipations.html')
