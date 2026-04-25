from django.shortcuts import render
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta


def home(request):
    if not request.user.is_authenticated:
        return render(request, 'dashboard/home.html')

    from clubhouse.models import Club, Event, Attendance, Survey
    from bulletin_board.models import Request as BulletinRequest
    from account.models import Profile

    profile = request.user.profile
    is_admin = profile.role == profile.Role.ADMIN
    is_officer_or_above = profile.role in (
        Profile.Role.ADMIN, Profile.Role.ADVISOR, Profile.Role.LEAD
    )

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)  # window used for "recent" check-in counts

    personal = {
        'points': profile.points,
        'events_attended': profile.events_attended_count,
        'club_count': (
            profile.club_member.all() | profile.faculty_advisor.all()
        ).distinct().count(),
        'surveys_done': Survey.objects.filter(attendee=request.user).count(),
    }

    # Upcoming events the user hasn't attended yet
    attended_pks = set(
        Attendance.objects.filter(user=request.user).values_list('event_id', flat=True)
    )
    upcoming_events = (
        Event.objects.filter(
            club__approved=True, club__denied=False,
            status=Event.Status.PUBLISHED,
            end_time__gte=now,
        )
        .select_related('club', 'location')
        .order_by('start_time')[:5]
    )

    club_analytics = None
    if is_officer_or_above:
        if is_admin:
            managed_clubs = Club.objects.filter(approved=True, denied=False)
        else:
            managed_clubs = Club.objects.filter(
                Q(officers=profile) | Q(advisors=profile),
                approved=True, denied=False,
            ).distinct()

        clubs_data = []
        for club in managed_clubs:
            published_events = club.events.filter(status=Event.Status.PUBLISHED)
            total_checkins = Attendance.objects.filter(event__club=club).count()
            recent_checkins = Attendance.objects.filter(
                event__club=club, checked_in_at__gte=thirty_days_ago
            ).count()
            avg_att = (
                published_events
                .annotate(cnt=Count('attendees'))
                .aggregate(avg=Avg('cnt'))
            )['avg'] or 0

            # Chart: last 6 published events
            chart_events = list(
                published_events
                .annotate(attendee_count=Count('attendees', distinct=True))
                .order_by('start_time')
                .values('title', 'attendee_count', 'point_value')
            )[-6:]

            # Pending requests
            pending_reqs = BulletinRequest.objects.filter(
                club=club, approval_status='-'
            ).count()

            # Top 5 members
            top_members = (
                Profile.objects.filter(club_member=club)
                .order_by('-points')[:5]
            )

            clubs_data.append({
                'club': club,
                'member_count': club.members.count(),
                'total_checkins': total_checkins,
                'recent_checkins': recent_checkins,
                'avg_attendance': round(avg_att, 1),
                'event_count': published_events.count(),
                'upcoming_count': published_events.filter(start_time__gt=now).count(),
                'pending_requests': pending_reqs,
                'chart_labels': [e['title'][:16] for e in chart_events],
                'chart_attendance': [e['attendee_count'] for e in chart_events],
                'top_members': top_members,
            })

        club_analytics = clubs_data

    return render(request, 'dashboard/home.html', {
        'personal': personal,
        'upcoming_events': upcoming_events,
        'attended_pks': attended_pks,
        'club_analytics': club_analytics,
        'is_officer_or_above': is_officer_or_above,
        'is_admin': is_admin,
    })