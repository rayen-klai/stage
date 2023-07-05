from importlib.metadata import files
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from user.models import Profile
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import JsonResponse

def custom_login_required(function=None):
    login_url = '/admin'  # Specify your custom login URL
    redirect_field_name = ''  # Specify your custom redirect field name

    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)

def admin_login(request):
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('/admin')
            else:
                return redirect('/formation')

        if request.method == 'POST' and 'signup_submit' in request.POST:
            email = request.POST.get('email')
            pwd = request.POST.get('pwd')
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            cin = request.POST.get('cin')
            org = request.POST.get('org')
            
            if not email or not pwd or not nom or not prenom or not cin or not org:
                error_message = "Veuillez remplir tous les champs !"
                return JsonResponse({'success': False, 'message': error_message})
            
            if Profile.objects.filter(email=email).exists():
                error_message = "Un compte avec cet e-mail existe déjà."
                return JsonResponse({'success': False, 'message': error_message})
            
            if Profile.objects.filter(cin=cin).exists():
                error_message = "Un compte avec ce cin existe déjà."
                return JsonResponse({'success': False, 'message': error_message})

            try:
                validate_email(email)
            except ValidationError as e:
                error_message = str(e)
                return JsonResponse({'success': False, 'message': error_message})
   
            cin_regex = RegexValidator(regex=r'^\d{8}$', message="CIN contient 8 chiffres.")
            try:
                cin_regex(cin)
            except ValidationError as e:
                error_message = str(e)
                return JsonResponse({'success': False, 'message': error_message})

            user = Profile(email=email, first_name=nom, last_name=prenom, cin=cin, organisme=org, role='Participant',)
            user.set_password(pwd)
            user.save()

            user_obj = authenticate(request, email=email, password=pwd)
            login(request, user_obj)

            return JsonResponse({'success': True, 'redirect_url': '/formation'})

        if request.method == 'POST' and 'signin_submit' in request.POST:
            email = request.POST.get('email')
            pwd = request.POST.get('pwd')
            user_obj = Profile.objects.filter(email=email)
            if not user_obj.exists():
                error_message = 'Vérifiez vos données'
                return JsonResponse({'success': False, 'message': error_message})
            
            user_obj = authenticate(request, email=email, password=pwd)

            if user_obj:
                login(request, user_obj)
                if user_obj.is_superuser:
                    return JsonResponse({'success': True, 'redirect_url': '/admin'})
                else:
                    return JsonResponse({'success': True, 'redirect_url': '/formation'})

            error_message = 'Mot de passe incorrect'
            return JsonResponse({'success': False, 'message': error_message})

        return render(request, 'front/signup.html')
    except Exception as e:
        print(e)

@custom_login_required
@staff_member_required
def Monprofile(request):
    user = request.user
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
        user.first_name = prenom 
        user.last_name = nom 
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
    return render(request, 'monprofile.html', context)



