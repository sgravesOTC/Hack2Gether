from django import forms
from .models import Club


class ClubEditForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'emoji', 'image']


class ClubCreateForm(forms.ModelForm):
    officer = forms.BooleanField(
        required=False,
        label='I am an officer of this club',
    )
    advisor = forms.BooleanField(
        required=False,
        label='I am a faculty advisor for this club',
    )

    class Meta:
        model = Club
        fields = ['name', 'description', 'emoji', 'image']
