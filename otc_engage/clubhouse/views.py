from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Club


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
    upcoming_events = club.events.order_by('start_time')
    is_member = club.members.filter(pk=request.user.profile.pk).exists()

    return render(request, 'clubhouse/club_detail.html', {
        'club': club,
        'upcoming_events': upcoming_events,
        'is_member': is_member,
        'section': 'clubhouse',
    })
