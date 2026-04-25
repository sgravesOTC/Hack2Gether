from django.shortcuts import render, redirect
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
        requests = Request.objects.order_by('complete', 'due_date')
    else:
        clubs = profile.club_officer.all() | profile.faculty_advisor.all()
        requests = Request.objects.filter(club__in=clubs).order_by('complete', 'due_date')

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
        'requests': requests,
        'reservations': reservations,
        'is_admin': profile.role == profile.Role.ADMIN,
        'club_count': club_count,
    })

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
