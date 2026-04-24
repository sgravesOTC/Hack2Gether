from django.urls import path
from . import views

app_name = 'clubhouse'

urlpatterns = [
    path('', views.club_list, name='club_list'),
    path('create/', views.club_create, name='club_create'),
    path('<slug:slug>/', views.club_detail, name='club_detail'),
    path('<slug:slug>/edit/', views.edit_club, name='edit_club'),
    path('<slug:slug>/approve/', views.approve_club, name='approve_club'),
]
