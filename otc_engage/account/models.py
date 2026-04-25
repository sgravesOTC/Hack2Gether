import uuid
import random
import string
from django.db import models


_CODE_CHARS = string.ascii_uppercase + string.digits


def _generate_short_code():
    return ''.join(random.choices(_CODE_CHARS, k=8))
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

    @property
    def events_attended_count(self):
        from clubhouse.models import Attendance  # local import, avoids circular import
        return Attendance.objects.filter(user=self.user).count()

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
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    checkin_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    short_code = models.CharField(max_length=8, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.short_code:
            # Regenerate on collision — statistically rare with 8-char alphanumeric space
            code = _generate_short_code()
            while Profile.objects.filter(short_code=code).exclude(pk=self.pk).exists():
                code = _generate_short_code()
            self.short_code = code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
