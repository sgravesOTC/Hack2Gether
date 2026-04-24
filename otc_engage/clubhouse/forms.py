from django import forms
from .models import Club
from account.models import Profile


class ClubEditForm(forms.ModelForm):
    officers = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.filter(role__in=[Profile.Role.LEAD, Profile.Role.STUDENT]),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Officers',
    )
    advisors = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.filter(role=Profile.Role.ADVISOR),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Faculty Advisors',
    )

    class Meta:
        model = Club
        fields = ['name', 'description', 'image', 'officers', 'advisors']


class ClubCreateForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'description', 'image', 'pending_advisor_name', 'pending_advisor_email']

    def __init__(self, *args, role=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = role
        self.fields['pending_advisor_name'].label = 'Faculty Advisor Name'
        self.fields['pending_advisor_email'].label = 'Faculty Advisor OTC Email'
        self.fields['pending_advisor_email'].help_text = 'Must be an @otc.edu address.'

        needs_advisor_info = role not in ('ADVISOR', 'ADMIN')
        if needs_advisor_info:
            self.fields['pending_advisor_name'].required = True
            self.fields['pending_advisor_email'].required = True
        else:
            del self.fields['pending_advisor_name']
            del self.fields['pending_advisor_email']

    def clean_pending_advisor_email(self):
        email = self.cleaned_data.get('pending_advisor_email', '')
        if email and not email.endswith('@otc.edu'):
            raise forms.ValidationError('Must be an @otc.edu email address.')
        return email
