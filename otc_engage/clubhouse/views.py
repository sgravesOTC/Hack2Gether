from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Club
from .forms import ClubEditForm, ClubCreateForm


@login_required
def club_list(request):
    profile = request.user.profile
    is_admin = profile.role == profile.Role.ADMIN

    if is_admin:
        all_clubs = Club.objects.all().order_by('approved', 'name')
    else:
        all_clubs = Club.objects.filter(approved=True)

    paginator = Paginator(all_clubs, 6)
    page_number = request.GET.get('page', 1)

    try:
        clubs = paginator.page(page_number)
    except EmptyPage:
        clubs = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        clubs = paginator.page(1)

    return render(request, 'clubhouse/club_list.html', {
        'clubs': clubs,
        'is_admin': is_admin,
        'section': 'clubhouse',
    })


@login_required
def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    profile = request.user.profile
    is_admin = profile.role == profile.Role.ADMIN

    if not club.approved and not is_admin:
        raise PermissionDenied

    upcoming_events = club.events.order_by('start_time')
    is_member = club.members.filter(pk=profile.pk).exists()
    can_edit = (
        club.officers.filter(pk=profile.pk).exists() or
        club.advisors.filter(pk=profile.pk).exists() or
        is_admin
    )

    return render(request, 'clubhouse/club_detail.html', {
        'club': club,
        'upcoming_events': upcoming_events,
        'is_member': is_member,
        'can_edit': can_edit,
        'is_admin': is_admin,
        'section': 'clubhouse',
    })


@login_required
def edit_club(request, slug):
    club = get_object_or_404(Club, slug=slug)
    profile = request.user.profile

    is_officer = club.officers.filter(pk=profile.pk).exists()
    is_advisor = club.advisors.filter(pk=profile.pk).exists()
    is_admin = profile.role == profile.Role.ADMIN

    if not (is_officer or is_advisor or is_admin):
        raise PermissionDenied

    if request.method == 'POST':
        form = ClubEditForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, 'Club updated successfully.')
            return redirect('clubhouse:club_detail', slug=club.slug)
    else:
        form = ClubEditForm(instance=club)

    return render(request, 'clubhouse/edit_club.html', {
        'form': form,
        'club': club,
        'is_admin': is_admin,
        'section': 'clubhouse',
    })


@login_required
def club_create(request):
    profile = request.user.profile

    form = ClubCreateForm(
        data=request.POST or None,
        files=request.FILES or None,
        role=profile.role,
    )

    if request.method == 'POST' and form.is_valid():
        club = form.save(commit=False)
        club.approved = False
        club.save()
        form.save_m2m()

        if profile.role == profile.Role.ADVISOR:
            club.advisors.add(profile)
        else:
            club.officers.add(profile)

        messages.success(request, f'{club.name} has been submitted for approval by Student Engagement.')
        return redirect('clubhouse:club_list')

    return render(request, 'clubhouse/create_club.html', {
        'form': form,
        'section': 'clubhouse',
    })


@login_required
def approve_club(request, slug):
    profile = request.user.profile
    if profile.role != profile.Role.ADMIN:
        raise PermissionDenied

    club = get_object_or_404(Club, slug=slug)

    if request.method == 'POST':
        club.approved = not club.approved
        club.save()
        status = 'approved' if club.approved else 'unapproved'
        messages.success(request, f'{club.name} has been {status}.')

    return redirect('clubhouse:club_detail', slug=club.slug)
