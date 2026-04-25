from django.contrib import admin
from .models import Club, Location, Event, Survey, SurveyQuestion, SurveyResponse, Attendance

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
    list_display = ['title', 'club', 'start_time', 'end_time', 'point_value','is_active']
    list_filter = ['club']
    search_fields = ['title']
    readonly_fields = ['token']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'checked_in_at')
    list_filter = ('event',)


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['event', 'prompt', 'question_type', 'order', 'required']
    list_filter = ['event', 'question_type']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['event', 'attendee', 'submitted_at', 'bonus_points_awarded']
    list_filter = ['event', 'bonus_points_awarded']

@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'question', 'text_answer', 'int_answer']
