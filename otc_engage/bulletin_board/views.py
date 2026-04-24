from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RequestForm
from .models import Request


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

    return render(request, 'bulletin_board/request_list.html', {
        'requests': requests,
        'section': 'bulletin_board',
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
