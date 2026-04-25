from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .forms import RequestForm, ReservationForm
from .models import Request, Reservation
from clubhouse.models import Event


def _requests_for_profile(profile):
    if profile.role == profile.Role.ADMIN:
        return Request.objects.all().order_by('complete', 'due_date')
    return Request.objects.filter(
        club__in=profile.club_officer.all() | profile.faculty_advisor.all()
    ).order_by('complete', 'due_date')

@login_required
def request_list(request):
    profile = request.user.profile
    requests = _requests_for_profile(profile)
    is_admin = profile.role == profile.Role.ADMIN

    return render(request, 'bulletin_board/request_list.html', {
        'requests': requests,
        'section': 'bulletin_board',
        'is_admin': is_admin,
    })

@login_required
def create_request(request):
    profile = request.user.profile
    form = RequestForm(data=request.POST or None, profile=profile)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Your request has been submitted.')
        return redirect('bulletin_board:request_list')

    return render(request, 'bulletin_board/create_request.html', {
        'form': form,
        'section': 'bulletin_board',
    })

@login_required
def set_request_approval(request, pk, status):
    profile = request.user.profile
    if profile.role != profile.Role.ADMIN:
        messages.error(request, 'You do not have permission to do that.')
        return redirect('bulletin_board:request_list')
    req = get_object_or_404(Request, pk=pk)
    req.approval_status = status
    req.save()
    return redirect('bulletin_board:request_list')

@login_required
def create_reservation(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    club = event.club
    profile = request.user.profile
    can_edit = (
        club.officers.filter(pk=profile.pk).exists() or
        club.advisors.filter(pk=profile.pk).exists() or
        profile.role == profile.Role.ADMIN
    )
    if not can_edit:
        raise PermissionDenied

    form = ReservationForm(
        data=request.POST or None,
        initial={'start_time': event.start_time, 'end_time': event.end_time},
    )
    if request.method == 'POST' and form.is_valid():
        reservation = form.save(commit=False)
        reservation.club = club
        reservation.event = event
        reservation.save()
        messages.success(request, 'Reservation submitted for approval.')
        return redirect('clubhouse:club_detail', slug=club.slug)

    return render(request, 'bulletin_board/create_reservation.html', {
        'form': form,
        'event': event,
        'club': club,
        'section': 'bulletin_board',
    })

@login_required
def set_reservation_approval(request, pk, approved):
    if request.user.profile.role != request.user.profile.Role.ADMIN:
        raise PermissionDenied
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.approved = approved
    reservation.save()
    return redirect('account:profile')
