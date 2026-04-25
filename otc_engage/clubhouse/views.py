import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Club, Event, Attendance, SurveyQuestion, Survey, SurveyResponse
from .forms import ClubEditForm, ClubCreateForm, CreateEventForm, NewRequestFormSet, SurveyQuestionFormSet, SurveySubmitForm
from django.http import HttpResponse


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

    is_member = club.members.filter(pk=profile.pk).exists()
    is_officer = club.officers.filter(pk=profile.pk).exists()
    can_edit = is_officer or club.advisors.filter(pk=profile.pk).exists() or is_admin
    if can_edit:
        upcoming_events = club.events.order_by('start_time')
    else:
        upcoming_events = club.events.filter(status=Event.Status.PUBLISHED).order_by('start_time')
    if can_edit:
        base_requests = club.requests.order_by('due_date')
        club_requests = {
            'pending': base_requests.filter(approval_status='-'),
            'approved': base_requests.filter(approval_status='O'),
            'denied': base_requests.filter(approval_status='X'),
        }
    else:
        club_requests = None
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
        club.officers.remove(request.user.profile)
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

    from bulletin_board.models import Request as BulletinRequest

    form = CreateEventForm(data=request.POST or None, club=club)
    request_formset = NewRequestFormSet(data=request.POST or None, prefix='req')

    if request.method == 'POST':
        form_valid = form.is_valid()
        formset_valid = request_formset.is_valid()

        if form_valid and formset_valid:
            filled_forms = [f for f in request_formset if f.is_filled()]

            if any(request_formset.errors):
                return render(request, 'clubhouse/create_event.html', {
                    'form': form,
                    'request_formset': request_formset,
                    'club': club,
                    'section': 'clubhouse',
                })

            event = form.save(commit=False)
            event.club = club
            event.status = Event.Status.SUBMITTED
            event.save()

            # Auto-create the event approval request
            BulletinRequest.objects.create(
                club=club,
                event=event,
                type=BulletinRequest.Type.EVENT,
                notes=f'Event approval requested for "{event.title}".',
                due_date=event.start_time,
            )

            # Handle linked existing request
            linked_request = form.cleaned_data.get('related_request')
            if linked_request:
                linked_request.due_date = event.start_time
                linked_request.save()

            # Handle additional support requests from formset
            for req_form in filled_forms:
                BulletinRequest.objects.create(
                    club=club,
                    type=req_form.cleaned_data['type'],
                    notes=req_form.cleaned_data['notes'],
                    due_date=event.start_time,
                )

            messages.success(request, f'"{event.title}" has been submitted for approval.')
            return redirect('clubhouse:club_detail', slug=club.slug)

        else:
            if not form_valid:
                messages.error(request, 'Event form has errors.')
            if not formset_valid:
                messages.error(request, 'Request formset has errors.')

    return render(request, 'clubhouse/create_event.html', {
        'form': form,
        'request_formset': request_formset,
        'club': club,
        'section': 'clubhouse',
    })


@login_required
def event_list(request):
    events = (
        Event.objects.filter(
            club__approved=True, club__denied=False,
            end_time__gte=timezone.now(),
            status=Event.Status.PUBLISHED,
        )
        .select_related('club', 'location')
        .order_by('start_time')
    )
    attended_pks = set(
        Attendance.objects.filter(user=request.user)
        .values_list('event_id', flat=True)
    )
    surveyed_pks = set(
        Survey.objects.filter(attendee=request.user)
        .values_list('event_id', flat=True)
    )
    return render(request, 'clubhouse/event_list.html', {
        'events': events,
        'attended_pks': attended_pks,
        'surveyed_pks': surveyed_pks,
        'section': 'clubhouse',
    })
def _can_edit_club(profile, club):
    return (
        club.officers.filter(pk=profile.pk).exists() or
        club.advisors.filter(pk=profile.pk).exists() or
        profile.role == profile.Role.ADMIN
    )

@login_required
def event_checkin_terminal(request, pk):
    from account.models import Profile
    from django.db.models import F

    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied

    result = None
    student_name = None

    if request.method == 'POST':
        raw = request.POST.get('code', '').strip().upper().replace(' ', '').replace('-', '')
        if len(raw) != 8:
            result = 'invalid'
        else:
            try:
                profile = Profile.objects.get(short_code=raw)
            except Profile.DoesNotExist:
                result = 'not_found'
            else:
                student_name = profile.user.get_full_name() or profile.user.username
                _, created = Attendance.objects.get_or_create(
                    event=event,
                    user=profile.user,
                )

                if created:
                    result = 'checked_in'

                    # Award points to the checking-in student
                    profile.points += event.point_value
                    profile.save(update_fields=['points'])

                    # Award 2 points to club officers
                    officer_profiles = event.club.officers.all()
                    officer_profiles.update(points=F('points') + 2)

                    # Award 1 point to regular members (non-officers)
                    member_profiles = event.club.members.exclude(
                        pk__in=event.club.officers.values_list('pk', flat=True)
                    )
                    member_profiles.update(points=F('points') + 1)

                else:
                    result = 'already_in'

    recent = event.attendees.select_related('user').order_by('-checked_in_at')[:10]
    return render(request, 'clubhouse/event_checkin_terminal.html', {
        'event': event,
        'result': result,
        'student_name': student_name,
        'recent': recent,
        'section': 'clubhouse',
    })
@login_required
def event_attendance(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied
    roster = event.attendees.select_related('user__profile').order_by('checked_in_at')
    return render(request, 'clubhouse/attendance.html', {
        'event': event,
        'roster': roster,
        'total': roster.count(),
        'section': 'clubhouse',
    })


@login_required
def submit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied
    if request.method == 'POST' and event.status == Event.Status.DRAFT:
        event.status = Event.Status.SUBMITTED
        event.save()
        from bulletin_board.models import Request as BulletinRequest
        BulletinRequest.objects.create(
            club=event.club,
            type=BulletinRequest.Type.OTHER,
            notes=f'Event "{event.title}" submitted for approval ({event.start_time.strftime("%b %-d, %Y")}). Please review and approve.',
            due_date=event.start_time,
        )
        messages.success(request, f'"{event.title}" submitted for approval.')
    return redirect('clubhouse:club_detail', slug=event.club.slug)


@login_required
def approve_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.profile.role != request.user.profile.Role.ADMIN:
        raise PermissionDenied
    if request.method == 'POST' and event.status == Event.Status.SUBMITTED:
        event.status = Event.Status.APPROVED
        event.save()
        messages.success(request, f'"{event.title}" approved.')
    return redirect('clubhouse:club_detail', slug=event.club.slug)


@login_required
def publish_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.profile.role != request.user.profile.Role.ADMIN:
        raise PermissionDenied
    if request.method == 'POST' and event.status == Event.Status.APPROVED:
        event.status = Event.Status.PUBLISHED
        event.save()
        messages.success(request, f'"{event.title}" published.')
    return redirect('clubhouse:club_detail', slug=event.club.slug)


@login_required
def event_attendance_export(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied
    roster = event.attendees.select_related('user__profile').order_by('checked_in_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{event.title}-attendance.csv"'
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'OTC Email', 'Checked In At'])
    for entry in roster:
        u = entry.user
        otc_email = u.profile.otc_email
        writer.writerow([
            u.first_name,
            u.last_name,
            u.email,
            otc_email if otc_email != u.email else '',
            entry.checked_in_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return response



@login_required
def edit_survey(request, pk):
    """Club officers/advisors/admins configure questions for an event's survey."""
    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied

    formset = SurveyQuestionFormSet(
        data=request.POST or None,
        instance=event,
    )
    if request.method == 'POST' and formset.is_valid():
        formset.save()
        messages.success(request, 'Survey updated.')
        return redirect('clubhouse:club_detail', slug=event.club.slug)

    return render(request, 'clubhouse/edit_survey.html', {
        'event': event,
        'formset': formset,
        'section': 'clubhouse',
    })


@login_required
def take_survey(request, pk):
    """Any attendee who checked in can fill out the survey once."""
    event = get_object_or_404(Event, pk=pk)
    user = request.user

    # Must have attended
    if not Attendance.objects.filter(event=event, user=user).exists():
        messages.error(request, 'You must check in to an event before filling out its survey.')
        return redirect('clubhouse:event_list')

    # Already submitted?
    if Survey.objects.filter(event=event, attendee=user).exists():
        messages.info(request, 'You have already submitted a survey for this event.')
        return redirect('clubhouse:event_list')

    questions = event.survey_questions.all()
    if not questions.exists():
        messages.info(request, 'This event has no survey questions.')
        return redirect('clubhouse:event_list')

    form = SurveySubmitForm(data=request.POST or None, questions=questions)

    if request.method == 'POST' and form.is_valid():
        survey = Survey.objects.create(event=event, attendee=user)
        for q in questions:
            raw = form.cleaned_data.get(f'q_{q.pk}')
            if raw is None:
                continue
            if q.question_type in (SurveyQuestion.QuestionType.STARS,
                                   SurveyQuestion.QuestionType.YESNO):
                SurveyResponse.objects.create(survey=survey, question=q, int_answer=int(raw))
            else:
                SurveyResponse.objects.create(survey=survey, question=q, text_answer=raw)

        # Award bonus points if the event has a nonzero point value
        bonus = max(1, event.point_value // 5)  # e.g. 10pts event → 2 bonus pts
        if bonus and not survey.bonus_points_awarded:
            profile = user.profile
            profile.points += bonus
            profile.save(update_fields=['points'])
            survey.bonus_points_awarded = True
            survey.save(update_fields=['bonus_points_awarded'])
            messages.success(request, f'Thanks! Survey submitted — you earned {bonus} bonus point{"s" if bonus != 1 else ""}.')
        else:
            messages.success(request, 'Survey submitted. Thanks for your feedback!')

        return redirect('clubhouse:event_list')

    return render(request, 'clubhouse/take_survey.html', {
        'event': event,
        'form': form,
        'section': 'clubhouse',
    })


@login_required
def survey_results(request, pk):
    """Club officers/advisors/admins view aggregated survey results."""
    event = get_object_or_404(Event, pk=pk)
    if not _can_edit_club(request.user.profile, event.club):
        raise PermissionDenied

    questions = event.survey_questions.prefetch_related('surveyresponse_set').all()
    surveys = Survey.objects.filter(event=event).count()

    results = []
    for q in questions:
        responses = SurveyResponse.objects.filter(question=q)
        if q.question_type == SurveyQuestion.QuestionType.TEXT:
            answers = list(responses.exclude(text_answer='').values_list('text_answer', flat=True))
            results.append({'question': q, 'type': 'text', 'answers': answers})
        elif q.question_type == SurveyQuestion.QuestionType.STARS:
            counts = {i: 0 for i in range(1, 6)}
            for r in responses:
                if r.int_answer:
                    counts[r.int_answer] = counts.get(r.int_answer, 0) + 1
            total = sum(counts.values())
            avg = round(sum(k * v for k, v in counts.items()) / total, 1) if total else None
            results.append({'question': q, 'type': 'stars', 'counts': counts, 'avg': avg, 'total': total})
        else:  # YESNO
            yes = responses.filter(int_answer=1).count()
            no = responses.filter(int_answer=0).count()
            results.append({'question': q, 'type': 'yesno', 'yes': yes, 'no': no})

    return render(request, 'clubhouse/survey_results.html', {
        'event': event,
        'results': results,
        'total_submissions': surveys,
        'section': 'clubhouse',
    })