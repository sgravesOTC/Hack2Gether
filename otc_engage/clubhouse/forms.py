from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Club, Event
from account.models import Profile
from bulletin_board.models import Request


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


class NewRequestForm(forms.Form):
    type = forms.ChoiceField(
        choices=[('', '---------')] + Request.Type.choices,
        required=False,
        label='Request Type',
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2}),
        required=False,
        label='Notes',
    )

    def clean(self):
        cleaned_data = super().clean()
        req_type = cleaned_data.get('type')
        req_notes = cleaned_data.get('notes')
        if bool(req_type) != bool(req_notes):
            raise forms.ValidationError('Fill in both type and notes, or leave both empty.')
        return cleaned_data

    def is_filled(self):
        return bool(self.cleaned_data.get('type') and self.cleaned_data.get('notes'))


NewRequestFormSet = forms.formset_factory(NewRequestForm, extra=1)


class CreateEventForm(forms.ModelForm):
    related_request = forms.ModelChoiceField(
        queryset=Request.objects.none(),
        required=False,
        label='Link to Existing Request',
        help_text="The selected request's due date will be updated to this event's start time.",
    )

    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time', 'point_value']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, club=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']
        if club is not None:
            self.fields['related_request'].queryset = Request.objects.filter(club=club, complete=False)

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time and start_time < timezone.now() + timedelta(days=5):
            raise forms.ValidationError('Events must be scheduled at least 5 days in advance.')
        return start_time

    def clean_point_value(self):
        point_value = self.cleaned_data.get('point_value', 0)
        if point_value > 10:
            raise forms.ValidationError('Please submit a request to Student Engagement to set a value higher than 10.')
        if point_value < 0:
            raise forms.ValidationError('Point values must be between 0 and 10.')
        return point_value
