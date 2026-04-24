from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'otc_email', 'role', 'points']
    list_filter = ['role']
    search_fields = ['user__username', 'otc_email']
