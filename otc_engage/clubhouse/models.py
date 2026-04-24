from django.db import models
from account.models import Profile

# Create your models here.
class Club(models.Model):
    name = models.CharField(max_length=50)
    advisors = models.ManyToManyField(
        Profile,
        related_name='faculty_advisor',
        blank=True,
    )
    officers = models.ManyToManyField(
        Profile,
        related_name='club_officer',
        blank=True,
    )
    description = models.TextField()
    members = models.ManyToManyField(
        Profile,
        related_name ='club_member',
        blank=True,
    )

class Location(models.Model):
    class Building(models.TextChoices):
        ICW = 'ICW','Information Commons West'
        IC = 'IC','Information Commons'
        ICE = 'ICE','Information Commons East'
        ITTC = 'ITTC','Industry and Transportation Technology Center'
        PMC = 'PMC', 'Plaster Manufacturing System'
        LNC = 'LNC', 'Linconln Hall'
        GRAFF = 'GRAFF', 'Graff Hall'
    
    building = models.CharField(max_length=5, choices=Building.choices)
    room_num= models.CharField(max_length=5)
    room_name= models.CharField(max_length=50, null=True, blank=True)

class Event(models.Model):
    title = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    club = models.ForeignKey(
        Club,
        related_name='events',
        on_delete=models.CASCADE,
    )
    location = models.ForeignKey(
        Location,
        related_name='events',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    point_value=models.IntegerField(default=0)

class Roster(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='roster',
    )
    attendees = models.ManyToManyField(
        Profile,
        related_name='rosters',
        blank=True,
    )

STARS = [(i, i) for i in range(1, 6)] 

class Survey(models.Model):
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='survey',
    )
    attendee = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='surveys')
    rating = models.PositiveSmallIntegerField(choices=STARS)
    feedback=models.TextField
    point_value=models.IntegerField(default=0)
    class Meta:
        unique_together = ('event', 'attendee')
