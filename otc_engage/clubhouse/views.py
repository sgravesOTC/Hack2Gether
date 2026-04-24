from django.shortcuts import render
from .models import Club
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
def club_list(request): # TODO: Add tags
    """
    Display a list of clubs
    """
    club_list = Club.objects.all()

    # Pagination
    paginator = Paginator(club_list, 6)
    page_number = request.GET.get('page', 1)

    # Hnadle pagination edge cases
    try:
        clubs = paginator.page(page_number)
    except EmptyPage:
        # If pag is too high, show last page
        articles = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # If page is invalid, show first page
        articles = paginator.page(1)

    return render(
        request,
        'clubhouse/club_list.html',
        {'clubs': clubs,'section':'clubhouse'}
    )