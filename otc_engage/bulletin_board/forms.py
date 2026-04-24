from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Request, Reservation
from clubhouse.models import Club


class RequestForm(forms.ModelForm):

    class Meta:
        model = Request
        fields = ['club', 'type', 'notes', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%dT%H:%M']
        if profile is not None:
            self.fields['club'].queryset = (
                profile.club_officer.filter(approved=True) |
                profile.faculty_advisor.filter(approved=True)
            ).distinct()
        else:
            self.fields['club'].queryset = Club.objects.none()

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now() + timedelta(weeks=1):
            raise forms.ValidationError(
                'Requests must be submitted at least one week in advance. '
                'For urgent requests, please contact Student Engagement directly.'
            )
        return due_date
