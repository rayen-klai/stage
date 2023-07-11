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
from django.views.decorators.csrf import csrf_exempt
from .forms import SignupForm,SigninForm
from jsonview.decorators import json_view
from django.template.context_processors import csrf
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.hashers import make_password
from gestionFormation.backends import EmailBackend


def custom_login_required(function=None):
    login_url = '/admin'  # Specify your custom login URL
    redirect_field_name = ''  # Specify your custom redirect field name

    return login_required(function, redirect_field_name=redirect_field_name, login_url=login_url)



from django.forms.utils import ErrorDict

"""
def admin_login(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])

            # Save the user object
            user.save() 
            return JsonResponse({'success': True})
        else:
            # Return the form errors as JSON response
            field_errors = form.errors.as_json()
            return JsonResponse({'success': False, 'field_errors': field_errors})
    else:
        form = SignupForm()
    return render(request, 'front/signup.html', {'form': form})
"""
from django.http import JsonResponse

def admin_login(request):
    form2 = SigninForm()
    form = SignupForm()
    if request.method == 'POST':
        if 'signin_submit' in request.POST:
            form2 = SigninForm(request.POST)
            if form2.is_valid():
                email = form2.cleaned_data['email']
                password = form2.cleaned_data['password']
                user = authenticate(request, email=email, password=password)
                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('/admin')
                    else:
                        return redirect('/formation')
            else:
                form2 = SigninForm(request.POST)
        else:
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.set_Role('Participant')
                user.save()
                login(request, user,backend='django.contrib.auth.backends.ModelBackend')                
                return JsonResponse({'success': True})
            else:
                field_errors = form.errors.as_json()
                return JsonResponse({'success': False, 'field_errors': field_errors})
    return render(request, 'front/signup.html', {'form': form, 'form2': form2})



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



