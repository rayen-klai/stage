from datetime import date
import datetime
from django.shortcuts import redirect, render
from django.http import HttpResponse 
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.core.files.storage import default_storage
from formation.models import formation
from datetime import datetime
from user.models import Profile
from datetime import date
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from django.utils.safestring import mark_safe
from datetime import timedelta, datetime, date
from django.shortcuts import render
from django.http import JsonResponse 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test





def custom_login_required(function=None):
    login_url = '/signup'  # Specify your custom login URL
    redirect_field_name = ''  # Specify your custom redirect field name
    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)

# Create your views here.
@csrf_exempt
def save_character(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        character = data.get('character')
        idq,j,qr = character.split("-")
        id = data.get('id')
        f = formation.objects.get(id=id)
        f.qr = qr
        f.save()
        response = {'message': 'Character saved successfully'}
        return JsonResponse(response)
    else:
        response = {'error': 'Invalid request method'}
        return JsonResponse(response, status=400)


def is_formateur(user):
    return user.is_authenticated and user.role == "Formateur"

@user_passes_test(is_formateur)
@custom_login_required
def presence(request, id, date2):
    today = date.today()
    today = today.strftime("%Y-%m-%d")
    if(date2==today):
        affqr=True
    else:
        affqr = False


    f = formation.objects.get(id=id)
    date_deb = f.date_deb  # Date de début
    date_fin = f.date_fin  # Date de fin
    jours = []
    current_date = date_deb
    i = 0
    j = 0
    while current_date <= date_fin:
        jours.append(str(current_date))
        current_date += timedelta(days=1)
        c = current_date.strftime("%Y-%m-%d")
        if c == date2:
            j = i
        i += 1
    
    l = []
    print(j)
    for cle, valeur in f.participants.items():
        print(valeur)
        print(valeur[j])
        l.append([Profile.objects.get(id=cle), valeur[j]])
    if request.method == 'POST' and 'prs' in request.POST:
        selected_values = request.POST.getlist('presence')
        for key in f.participants:
            if key in selected_values:
                f.participants[key][j] = 1
            else:
                f.participants[key][j] = 0
        f.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
    context = {
        "jours": jours,
        "datecrnt": date2,
        "f": f,
        "participant": l,
        "affqr" : affqr, 
        "jq" : j , 
    }
    return render(request, 'front/presence.html', context)

 
@user_passes_test(is_formateur)
@custom_login_required
def cal(request):
    today = date.today()
    user = request.user
    formations_list = formation.objects.all()
    matching_formations = []
    form_enc = []
    for form in formations_list:
        if form.formateur == user:
            matching_formations.append(form) 
            if form.date_deb <= today <= form.date_fin:
                form_enc.append(form)  

    context = {
        "events":matching_formations,
        "enc" : form_enc,
    }
    return render(request,'front/calendrier.html',context)
 
def all_events(request): 
    user = request.user
    formations_list = formation.objects.all()
    all_events = []
    for form in formations_list:
        if form.formateur == user:
            all_events.append(form)                                                                                                  
    out = []                                                                                                             
    for event in all_events:
        nouvelle_date_fin = event.date_fin + timedelta(days=1)                                                                                             
        out.append({                                                                                                     
            'title': event.titre,                                                                                         
            'id': event.id,                                                                                              
            'start': event.date_deb.strftime("%m/%d/%Y"),                                                         
            'end': nouvelle_date_fin.strftime("%m/%d/%Y"),
            'qr' : event.qr                                                         
        })                                                                                                               
    return JsonResponse(out, safe=False) 
 

def acc(request):
    today = date.today().strftime("%Y-%m-%d")
    formations = formation.objects.filter(date_fin__gt=today)
    users = Profile.objects.filter(role='Formateur')
    return render(request, 'accueill.html', {'formations': formations , 'formateurs' : users })


def nosformations(request):
    today = date.today()
    formations = formation.objects.all()
    formations_filtrées = []
    
    for f in formations:
        jour_calcule = f.date_deb + (f.date_fin - f.date_deb) / 2
        
        if today >= jour_calcule:
            formations_filtrées.append(f)
    print(formations_filtrées)
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
    today = date.today().strftime("%Y-%m-%d")
    formations = formation.objects.filter(date_fin__gt=today)
    formations = formations.exclude(id__in=[f.id for f in formations_filtrées])
    return render(request, 'front/nosFormations.html', {'formations': formations})

def nosformateurs(request):
    users = Profile.objects.filter(role='Formateur')
    return render(request,'front/nosFormateurs.html',{'formateurs' : users})

def signup(request):
    return render(request,'front/signup.html')

def reset(request):
    return render(request,'front/reset.html')

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

def is_participant(user):
    return user.is_authenticated and user.role == "Participant"



@user_passes_test(is_participant)
@custom_login_required
def evaluation(request,id):
    f = formation.objects.get(id=id)
    if request.method == 'POST':
        l=[]
        r1 = request.POST.get('r1')
        r2 = request.POST.get('r2')
        r3 = request.POST.get('r3')
        r4 = request.POST.get('r4')
        r5 = request.POST.get('r5')
        r6 = request.POST.get('r6')
        r7 = request.POST.get('r7')
        r8 = request.POST.get('r8')
        r9 = request.POST.get('r9')
        r10 = request.POST.get('r10')
        if not r1 or not r2 or not r3 or not r4 or not r5 or not r6 or not r7 or not r8 or not r9 or not r10:
            error_message = "Veuillez sélectionner au moins un bouton radio pour chaque ligne."
            return render(request, 'front/evaluation.html', {'f' : f , 'error_message': error_message})
        else:
            l.append(r1)
            l.append(r2)
            l.append(r3)
            l.append(r4)
            l.append(r5)
            l.append(r6)
            l.append(r7)
            l.append(r8)
            l.append(r9)
            l.append(r10)
            f.evaluation[request.user.id] = l
            f.save()
            return redirect('part')

    return render(request, 'front/evaluation.html', {'f' : f})



@user_passes_test(is_participant)
@custom_login_required
def part(request):
    today = date.today()
    user2 = request.user
    formations_list = formation.objects.all()
    enc = []
    ter = []
    enatt = []
    for form in formations_list:
        participants = form.participants
        if str(user2.id) in participants.keys():
            if participants[str(user2.id)] == 0:
                enatt.append(form) 
            elif(isinstance(participants[str(user2.id)], list)):
                d1 = datetime.strptime(str(today), "%Y-%m-%d")
                d2 = datetime.strptime(str(form.date_fin), "%Y-%m-%d")
                if d2 >= d1:
                    enc.append(form)
                else:
                    ter.append(form)
    return render(request,'front/mesParticipations.html',{'enc' : enc , 'ter' : ter , 'enatt' : enatt})


def endpoint(request):
    if request.method == 'POST':
        # Retrieve the parameters from the request body
        str = request.POST.get('s')
        print(str)
        response_data = {'message': 'Request received successfully'}
        return JsonResponse(response_data)

    response_data = {'error': 'Unsupported request method'}
    return JsonResponse(response_data, status=405)

@api_view(['POST'])
def getRoutes(request):
   routes = [{
       'Endpoint': '/api/endpoint',
       'method': 'POST',
       'body': {'body': ""},
       'description': 'SEND'
   }]
   return Response(routes)


@api_view(['POST'])
def pres(request):
    s = request.data.get('str')  # Access the 'str' value from the request data
    user_id = request.data.get('user')  # Access the 'str' value from the request data
    id,j,qr = s.split("-")
    print(qr)
    formation_instance = formation.objects.get(id=id)
    if(formation_instance.qr != qr):
        response_data = {'message': 'QrCode invalide .'}
    elif str(user_id) not in formation_instance.participants:
        response_data = {'message': 'Vous n avez pas participe a cette formation.'}
    elif ( formation_instance.participants[str(user_id)][int(j)] == 1):
        response_data = {'message': 'Vous etes deja marque present.'}
    else:
        formation_instance.participants[str(user_id)][int(j)] = 1
        formation_instance.save()
        response_data = {'message': 'L operation s est terminee avec succes.'}
    return Response(response_data)