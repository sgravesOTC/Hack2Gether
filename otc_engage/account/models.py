from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_otc_email(value):
    if not value.endswith('@otc.edu'):
        raise ValidationError('Email must end with @otc.edu.')


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    otc_email = models.EmailField(
        unique=True, 
        validators=[validate_otc_email]
    )
    points = models.IntegerField(default=0)

    class Role(models.TextChoices):
        ADMIN = 'ADMIN','Student Engagement'
        ADVISOR = 'ADVISOR','Faculty Advisor'
        LEAD = 'LEAD','Club Officer'
        STUDENT = 'STUDENT','Student'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    