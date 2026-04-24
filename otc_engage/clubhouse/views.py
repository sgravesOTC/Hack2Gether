from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Club
from .forms import ClubEditForm


@login_required
def club_list(request):
    all_clubs = Club.objects.all()

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
        'section': 'clubhouse',
    })


@login_required
def club_detail(request, slug):
    club = get_object_or_404(Club, slug=slug)
    profile = request.user.profile
    upcoming_events = club.events.order_by('start_time')
    is_member = club.members.filter(pk=profile.pk).exists()
    can_edit = (
        club.officers.filter(pk=profile.pk).exists() or
        club.advisors.filter(pk=profile.pk).exists() or
        profile.role == profile.Role.ADMIN
    )

    return render(request, 'clubhouse/club_detail.html', {
        'club': club,
        'upcoming_events': upcoming_events,
        'is_member': is_member,
        'can_edit': can_edit,
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
        'section': 'clubhouse',
    })
