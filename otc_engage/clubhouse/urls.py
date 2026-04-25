from django.urls import path
from . import views

app_name = 'clubhouse'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('create/', views.club_create, name='club_create'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/qr/', views.generate_qr_view, name='generate_qr'),
    path('events/<int:pk>/qr-page/', views.event_qr_page, name='event_qr_page'),
    path('events/checkin/<uuid:token>/', views.checkin_view, name='event_checkin'),
    path('checkin/', views.manual_checkin, name='manual_checkin'),
    path('<slug:slug>/', views.club_detail, name='club_detail'),
    path('<slug:slug>/edit/', views.edit_club, name='edit_club'),
    path('<slug:slug>/approve/', views.approve_club, name='approve_club'),
    path('<slug:slug>/deny/', views.deny_club, name='deny_club'),
    path('<slug:slug>/undo-deny/', views.undo_deny_club, name='undo_deny_club'),
    path('<slug:slug>/join/', views.join_club, name='join_club'),
    path('<slug:slug>/leave/', views.leave_club, name='leave_club'),
    path('<slug:slug>/apply-officer/', views.apply_officer, name='apply_officer'),
    path('<slug:slug>/approve-officer/<int:profile_pk>/', views.approve_officer_application, name='approve_officer_application'),
    path('<slug:slug>/create-event/', views.create_event, name='create_event'),
]
