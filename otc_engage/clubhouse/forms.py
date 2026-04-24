from django import forms
from .models import Club, Event
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
    
class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time', 'point_value']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean_point_value(self):
        point_value = self.cleaned_data.get('point_value', 0)
        if point_value > 10:
            raise forms.ValidationError('Please submit a request to Student Engagement to set a value higher than 10.')
        return point_value
