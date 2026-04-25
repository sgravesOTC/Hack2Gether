from django.db import models
from django.utils import timezone
from clubhouse.models import Club, Location, Event

class Request(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    event = models.ForeignKey(
        'clubhouse.Event',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='approval_requests'
    )

    class Type(models.TextChoices):
        IT = 'IT','Information Technology'
        MONEY = 'FINANCE', 'Finance'
        CLEAN = 'CUSTODIAL','Custodial'
        SAFE = 'SECURITY','Security and Safety'
        EVENT = 'EVENT', 'Event Approval'
        OTHER = 'OTHER', 'See notes'
    type = models.CharField(max_length=10, choices=Type.choices)
    notes = models.TextField()
    complete = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(default=timezone.now)
    class Approval(models.TextChoices):
        DENIED = 'X','Denied'
        APPROVED = 'O','Approved'
        PENDING = '-','Pending'
    approval_status = models.CharField(max_length=1,choices=Approval.choices, default=Approval.PENDING)

class Reservation(models.Model):
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='reservations'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='reservations'
    )
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)