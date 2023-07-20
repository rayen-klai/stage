from datetime import date, timedelta
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
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import random
from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None



#Opens up page as PDF
class ViewPDF(View):
	
    def get(self, request,id, *args, **kwargs):
        f  = formation.objects.get(id=id)
        data = {
            "f" : f,
            "eval" : f.evaluation , 
            }
        pdf = render_to_pdf('front/pdf_template.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


#Automaticly downloads to PDF file
class DownloadPDF(View):
    def get(self, request, *args, **kwargs):
        data = {
            "company": "Dennnis Ivanov Company",
            "address": "123 Street name",
            "city": "Vancouver",
            "state": "WA",
            "zipcode": "98663",


            "phone": "555-555-2345",
            "email": "youremail@dennisivy.com",
            "website": "dennisivy.com",
            }
        pdf = render_to_pdf('front/pdf_template.html', data)
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % ("12341231")
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response



def custom_login_required(function=None):
    login_url = '/signup'  # Specify your custom login URL
    redirect_field_name = ''  # Specify your custom redirect field name

    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)

def validate_price(price_input):
    try:
        price_float = float(price_input)
        return True
    except ValueError:
        return False


@staff_member_required
@custom_login_required
def presence2(request,id, date2):
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
    return render(request, 'admin/formation/presence.html', context)


@custom_login_required
@staff_member_required
def index(request):
    return render(request,'admin/formation/index.html', {'formations': formation.objects.all()})


@custom_login_required
@staff_member_required
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
        random_char = random.choice('abcdefghijklmnopqrstuvwxyz')
        nouvelle_formation = formation(
            titre=titre,
            nbp=nombre_place,
            prx=prix,
            date_deb=date_debut,
            date_fin=date_fin,
            formateur=frm,
            qr= random_char,
        )
        nouvelle_formation.save()
        return redirect('index')

    return render(request, 'admin/formation/new.html',{'users' : Profile.objects.all()})


@custom_login_required
@staff_member_required
def update(request):
    return render(request,'admin/formation/update.html')


@custom_login_required
@staff_member_required
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
        nombre_jours = (f.date_fin - f.date_deb).days 
        liste_zero = [0] * (nombre_jours + 1)
        f.participants[request.POST.get('btn_acc')] = liste_zero 
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
    jss = {1 : [1,1] , 2 : {20,5} } ; 
    today =date.today().strftime("%Y-%m-%d")
    return render(request,'admin/formation/detaille.html',{'f' : f , 'users' : Profile.objects.all(),'par_enatt' : participants_enatt , 'par_enc' : participants_enc , 'nbpd' : nbpd , 'nbpr' : nbpr , 'today' : today ,'jss' : jss})