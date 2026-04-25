import uuid
from django.db import models
from django.utils.text import slugify
from account.models import Profile
from django.conf import settings
from django.utils import timezone


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
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    emoji = models.CharField(max_length=10, blank=True, default='🏛️')
    image = models.ImageField(upload_to='club_images/', null=True, blank=True)
    officer_applicants = models.ManyToManyField(
        Profile,
        related_name='officer_applications',
        blank=True,
    )
    approved = models.BooleanField(default=False)
    denied = models.BooleanField(default=False)
    pending_advisor_name = models.CharField(max_length=100, blank=True, default='')
    pending_advisor_email = models.EmailField(blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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

    def __str__(self):
        if self.room_name:
            return f'{self.building} {self.room_num} — {self.room_name}'
        return f'{self.building} {self.room_num}'

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
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    point_value=models.IntegerField(default=0)
    
    def is_active(self):
        return self.start_time<= timezone.now() <= self.end_time
    
    def __str__(self):
        return self.title
    
class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event','user')
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} @ {self.event}'
    


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
