from django.urls import path
from . import views

app_name = 'clubhouse'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('create/', views.club_create, name='club_create'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/submit/', views.submit_event, name='submit_event'),
    path('events/<int:pk>/approve/', views.approve_event, name='approve_event'),
    path('events/<int:pk>/publish/', views.publish_event, name='publish_event'),
    path('events/<int:pk>/complete/', views.complete_event, name='complete_event'),
    path('events/<int:pk>/terminal/', views.event_checkin_terminal, name='event_checkin_terminal'),
    path('events/<int:pk>/attendance/', views.event_attendance, name='event_attendance'),
    path('events/<int:pk>/attendance/export/', views.event_attendance_export, name='event_attendance_export'),
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
    path('events/<int:pk>/survey/edit/', views.edit_survey, name='edit_survey'),
    path('events/<int:pk>/survey/take/', views.take_survey, name='take_survey'),
    path('events/<int:pk>/survey/results/', views.survey_results, name='survey_results'),
]
