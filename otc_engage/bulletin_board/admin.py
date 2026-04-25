from django.contrib import admin
from .models import Request, Reservation

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['club', 'type', 'complete', 'created', 'updated']
    list_filter = ['type', 'complete', 'club']
    search_fields = ['notes']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['club', 'location', 'event', 'start_time', 'end_time', 'approved']
    list_filter = ['approved', 'club']
