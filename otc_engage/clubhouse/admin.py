from django.contrib import admin
from .models import Club, Location, Event, Roster, Survey

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['advisors', 'officers', 'members']
    fieldsets = [
        (None, {'fields': ['name', 'slug', 'description']}),
        ('Icon', {'fields': ['emoji', 'image'], 'description': 'Choose an emoji OR upload an image. Image takes priority if both are set.'}),
        ('Members', {'fields': ['advisors', 'officers', 'members']}),
    ]

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['building', 'room_num', 'room_name']
    list_filter = ['building']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'start_time', 'end_time', 'point_value']
    list_filter = ['club']
    search_fields = ['title']

@admin.register(Roster)
class RosterAdmin(admin.ModelAdmin):
    list_display = ['event']
    filter_horizontal = ['attendees']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['event', 'attendee', 'rating', 'point_value']
    list_filter = ['rating']
