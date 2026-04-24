from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Club, Event
from .forms import ClubEditForm, ClubCreateForm, CreateEventForm


@login_required
def club_list(request):
    profile = request.user.profile
    is_admin = profile.role == profile.Role.ADMIN

    if is_admin:
        all_clubs = Club.objects.all().order_by('approved', 'denied', 'name')
    else:
        all_clubs = Club.objects.filter(approved=True, denied=False)

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

    if (not club.approved or club.denied) and not is_admin:
        raise PermissionDenied

    upcoming_events = club.events.order_by('start_time')
    is_member = club.members.filter(pk=profile.pk).exists()
    is_officer = club.officers.filter(pk=profile.pk).exists()
    can_edit = is_officer or club.advisors.filter(pk=profile.pk).exists() or is_admin
    club_requests = club.requests.order_by('complete', 'due_date') if can_edit else None
    has_applied = club.officer_applicants.filter(pk=profile.pk).exists()

    return render(request, 'clubhouse/club_detail.html', {
        'club': club,
        'upcoming_events': upcoming_events,
        'is_member': is_member,
        'is_officer': is_officer,
        'can_edit': can_edit,
        'is_admin': is_admin,
        'club_requests': club_requests,
        'has_applied': has_applied,
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
        club.members.add(profile)

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
        club.denied = False
        club.save()
        status = 'approved' if club.approved else 'unapproved'
        messages.success(request, f'{club.name} has been {status}.')

    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def deny_club(request, slug):
    profile = request.user.profile
    if profile.role != profile.Role.ADMIN:
        raise PermissionDenied

    club = get_object_or_404(Club, slug=slug)

    if request.method == 'POST':
        club.denied = True
        club.approved = False
        club.save()
        messages.success(request, f'{club.name} has been denied.')

    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def undo_deny_club(request, slug):
    profile = request.user.profile
    if profile.role != profile.Role.ADMIN:
        raise PermissionDenied

    club = get_object_or_404(Club, slug=slug)

    if request.method == 'POST':
        club.denied = False
        club.save()
        messages.success(request, f'{club.name} has been restored to pending.')

    return redirect('clubhouse:club_detail', slug=club.slug)

@login_required
def join_club(request, slug):
    club = get_object_or_404(Club, slug=slug, approved=True, denied=False)
    if request.method == 'POST':
        club.members.add(request.user.profile)
    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def leave_club(request, slug):
    club = get_object_or_404(Club, slug=slug)
    if request.method == 'POST':
        club.members.remove(request.user.profile)
    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def apply_officer(request, slug):
    club = get_object_or_404(Club, slug=slug, approved=True, denied=False)
    if request.method == 'POST':
        profile = request.user.profile
        if club.officer_applicants.filter(pk=profile.pk).exists():
            club.officer_applicants.remove(profile)
        else:
            club.officer_applicants.add(profile)
    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def approve_officer_application(request, slug, profile_pk):
    club = get_object_or_404(Club, slug=slug)
    profile = request.user.profile
    if not (club.officers.filter(pk=profile.pk).exists() or
            club.advisors.filter(pk=profile.pk).exists() or
            profile.role == profile.Role.ADMIN):
        raise PermissionDenied
    if request.method == 'POST':
        applicant = get_object_or_404(club.officer_applicants, pk=profile_pk)
        club.officer_applicants.remove(applicant)
        club.officers.add(applicant)
    return redirect('clubhouse:club_detail', slug=club.slug)


@login_required
def create_event(request, slug):
    club = get_object_or_404(Club, slug=slug, approved=True, denied=False)
    profile = request.user.profile
    can_edit = (
        club.officers.filter(pk=profile.pk).exists() or
        club.advisors.filter(pk=profile.pk).exists() or
        profile.role == profile.Role.ADMIN
    )
    if not can_edit:
        raise PermissionDenied

    form = CreateEventForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        event = form.save(commit=False)
        event.club = club
        event.save()
        messages.success(request, f'"{event.title}" has been created.')
        return redirect('clubhouse:club_detail', slug=club.slug)

    return render(request, 'clubhouse/create_event.html', {
        'form': form,
        'club': club,
        'section': 'clubhouse',
    })


@login_required
def event_list(request):
    events = (
        Event.objects.filter(club__approved=True, club__denied=False, start_time__gte=timezone.now())
        .select_related('club', 'location')
        .order_by('start_time')
    )
    return render(request, 'clubhouse/event_list.html', {
        'events': events,
        'section': 'clubhouse',
    })

