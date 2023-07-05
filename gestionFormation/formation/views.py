from datetime import date
from ipaddress import summarize_address_range
import os
from django.shortcuts import redirect, render
from django.http import HttpResponse 
# Create your views here.
from user.models import Profile 
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import formation
from user.models import Profile
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import cv2


def validate_price(price_input):
    try:
        price_float = float(price_input)
        return True
    except ValueError:
        return False


def index(request):
    return render(request,'admin/formation/index.html', {'formations': formation.objects.all()})


def new(request):
    if request.method == 'POST':
        titre = request.POST.get('titre')
        id_formateur = request.POST.get('formateur')
        nombre_place = request.POST.get('nombrePlace')
        prix = request.POST.get('prix')
        date_debut = request.POST.get('dateDebut')
        date_fin = request.POST.get('dateFin')

        if not titre or not id_formateur or not nombre_place or not prix or not date_debut or not date_fin or id_formateur=='0' :
            messages.error(request, "Veuillez remplir tous les champs !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not nombre_place.isnumeric() or int(nombre_place) <= 0:
            messages.error(request, "Le nombre de places doit être un nombre entier positif !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not validate_price(prix) or float(prix) <= 0:
            messages.error(request, "Le prix doit être un nombre positif !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        frm = Profile.objects.get(id=id_formateur)

        nouvelle_formation = formation(
            titre=titre,
            nbp=nombre_place,
            prx=prix,
            date_deb=date_debut,
            date_fin=date_fin,
            formateur=frm,
        )
        nouvelle_formation.save()
        return redirect('index')

    return render(request, 'admin/formation/new.html',{'users' : Profile.objects.all()})

def update(request):
    return render(request,'admin/formation/update.html')

def detaille(request,id):
    f = formation.objects.get(id=id)
    participants = f.participants  
    participants_enatt = {key: value for key, value in participants.items() if value == 0}    
    participants_enc = {key: value for key, value in participants.items() if value != 0}
    user_ids_enatt = participants_enatt.keys()
    participants_enatt = [Profile.objects.get(id=key) for key in user_ids_enatt]
    user_ids_enc = participants_enc.keys()
    participants_enc = [Profile.objects.get(id=key) for key in user_ids_enc]

    nbpr = len(participants_enc)
    nbpd = f.nbp -  len(participants_enc)

    if request.method == 'POST' and 'btn_sup' in request.POST:
        f.delete()
        return render(request,'admin/formation/index.html',{'formations' : formation.objects.all })

    if request.method == 'POST' and 'btn_ats' in request.POST:
        user = Profile.objects.get(id=request.POST.get('btn_ats'))
        template = cv2.imread("staticfiles/attestation_template.png")
        nom_pre = f"{user.last_name} {user.first_name}"
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
        
        path = 'staticfiles/attestation/'+ frm +f'/{user.first_name}{user.last_name}.jpg'
        cv2.imwrite(path,template)

    if request.method == 'POST' and 'btn_acc' in request.POST:
        participants[request.POST.get('btn_acc')] = 1
        f.participants = participants
        f.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if request.method == 'POST' and 'btn_ret' in request.POST:
        participants.pop(str(request.POST.get('btn_ret')), None)
        f.participants = participants
        f.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    if request.method == 'POST' and 'btn_mod' in request.POST:
        titre = request.POST.get('titre')
        id_formateur = request.POST.get('formateur')
        nombre_place = request.POST.get('nombrePlace')
        prix = request.POST.get('prix')
        date_debut = request.POST.get('dateDebut')
        date_fin = request.POST.get('dateFin')

        if not titre or not id_formateur or not nombre_place or not prix or not date_debut or not date_fin or id_formateur=='0' :
            messages.error(request, "Veuillez remplir tous les champs !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not nombre_place.isnumeric() or int(nombre_place) <= 0:
            messages.error(request, "Le nombre de places doit être un nombre entier positif !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
       
        if not validate_price(prix) or float(prix) <= 0:
            messages.error(request, "Le prix doit être un nombre positif !")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
       
        frm = Profile.objects.get(id=id_formateur)
        f.titre = titre 
        f.formateur = frm
        f.nbp = nombre_place
        f.prx = prix
        f.date_deb  = date_debut
        f.date_fin = date_fin
        f.save() 
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request,'admin/formation/detaille.html',{'f' : f , 'users' : Profile.objects.all(),'par_enatt' : participants_enatt , 'par_enc' : participants_enc , 'nbpd' : nbpd , 'nbpr' : nbpr})