from django.urls import path
from . import views

app_name = 'clubhouse'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('<slug:slug>/', views.club_detail, name='club_detail'),
    path('<slug:slug>/edit/', views.edit_club, name='edit_club'),
]
