import io
import qrcode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ProfileRegistrationForm, UserEditForm, ProfileEditForm
from bulletin_board.models import Request, Reservation


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = ProfileRegistrationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return redirect('account:login')
    else:
        user_form = UserRegistrationForm()
        profile_form = ProfileRegistrationForm()
    return render(
        request,
        'account/register.html',
        {'user_form':user_form, 'profile_form':profile_form, 'section':'account'}
    )

@login_required
def profile(request):
    profile = request.user.profile
    if profile.role == profile.Role.ADMIN:
        base_requests = Request.objects.all()
    else:
        clubs = profile.club_officer.all() | profile.faculty_advisor.all()
        base_requests = Request.objects.filter(club__in=clubs)

    club_requests = {
        'pending': base_requests.filter(approval_status='-').order_by('due_date'),
        'approved': base_requests.filter(approval_status='O').order_by('due_date'),
        'denied': base_requests.filter(approval_status='X').order_by('due_date'),
    }

    club_count = (
        profile.club_member.all() | profile.faculty_advisor.all()
    ).distinct().count()

    reservations = (
        Reservation.objects.select_related('event', 'club', 'location').order_by('event__start_time')
        if profile.role == profile.Role.ADMIN
        else None
    )

    return render(request, 'account/profile.html', {
        'profile': profile,
        'club_requests': club_requests,
        'reservations': reservations,
        'is_admin': profile.role == profile.Role.ADMIN,
        'club_count': club_count,
    })

@login_required
def my_qr_page(request):
    profile = request.user.profile
    return render(request, 'account/my_qr.html', {
        'profile': profile,
        'section': 'account',
    })


@login_required
def my_qr_image(request):
    profile = request.user.profile
    img = qrcode.make(profile.short_code)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance = request.user,
            data = request.POST
        )
        profile_form = ProfileEditForm(
            instance = request.user.profile,
            data = request.POST,
            files = request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'There was an error updating your profile.')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance = request.user.profile)
    return render(
        request,
        'account/edit_profile.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
            'section': 'account',
        }
    )
