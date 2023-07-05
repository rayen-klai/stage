from django import forms
from .models import SignupModel  # Assuming you have a SignupModel defined in models.py

class SignupForm(forms.ModelForm):
    class Meta:
        model = SignupModel  # Replace `SignupModel` with your actual model name
        fields = ['nom', 'prenom', 'cin', 'org', 'email', 'pwd']  # Specify the fields you want to include in the form
        labels = {
            'pwd': 'Mot de passe',  # Customize field labels if needed
        }
        widgets = {
            'pwd': forms.PasswordInput(),  # Use password input widget for password field
        }
