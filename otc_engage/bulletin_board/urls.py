from django.urls import path
from . import views

app_name = 'bulletin_board'

urlpatterns = [
    path('requests/', views.request_list, name='request_list'),
    path('requests/new/', views.create_request, name='create_request'),
    path('requests/<int:pk>/approve/', views.set_request_approval, {'status': 'O'}, name='approve_request'),
    path('requests/<int:pk>/deny/', views.set_request_approval, {'status': 'X'}, name='deny_request'),
    path('reservations/<int:event_pk>/new/', views.create_reservation, name='create_reservation'),
    path('reservations/<int:pk>/approve/', views.set_reservation_approval, {'approved': True}, name='approve_reservation'),
    path('reservations/<int:pk>/deny/', views.set_reservation_approval, {'approved': False}, name='deny_reservation'),
]
