from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    """
    User Registration Form. 
    """
    password = forms.CharField(
        label = 'Password',
        widget = forms.PasswordInput
    )
    password2 = forms.CharField(
        label = 'Repeat Password',
        widget = forms.PasswordInput
    )
    class Meta:
        model = get_user_model()
        fields = ['username','first_name','last_name','email']
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']
    
    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email already in use.')
        return data
    
class ProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['otc_email']

