from django import forms
from crispy_forms.helper import FormHelper
from user.models import Profile
from django import forms
from django.contrib.auth import authenticate
from user.models import Profile

class SigninForm(forms.ModelForm):
    password = forms.CharField(
        max_length=100, 
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = "Email"
        self.fields['email'].widget.attrs.update({'style': 'width: 300px;'})

    def clean(self):
        password = self.cleaned_data['password']

        email = self.cleaned_data['email']

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                self.add_error('email', "Email ou mot de passe incorrect.")
                self.add_error('password', "Email ou mot de passe incorrect.")

    class Meta:
        model = Profile
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }

    
class SignupForm(forms.ModelForm):
    password = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].label = "Prénom"
        self.fields['last_name'].label = "Nom de famille"
        self.fields['cin'].label = "CIN"
        self.fields['organisme'].label = "Organisme"
        self.fields['email'].label = "Email"
        self.fields['first_name'].widget.attrs.update({'style': 'width: 300px;'})

    def clean_cin(self):
        cin = self.cleaned_data['cin']
        if not cin.isdigit() or len(cin) != 8:
            raise forms.ValidationError("Le CIN doit être un numéro à 8 chiffres.")
        return cin

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name.isalpha() and not first_name.isspace():
            raise forms.ValidationError("Le prénom ne doit contenir que des caractères alphabétiques.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name.isalpha() and not last_name.isspace():
            raise forms.ValidationError("Le nom  ne doit contenir que des caractères alphabétiques.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.pk is None and Profile.objects.filter(email=email).exists():
            raise forms.ValidationError("L'email existe déjà.")
        return email

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'cin', 'organisme', 'email', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom de famille'}),
            'cin': forms.TextInput(attrs={'placeholder': 'CIN'}),
            'organisme': forms.TextInput(attrs={'placeholder': 'Organisme'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
