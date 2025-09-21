from django.shortcuts import render
from recruiting.models import Listing


def index(request):
    """Recruiting index view: show active job listings."""
    listings = Listing.objects.filter(is_active=True).order_by('-posted_date')[:20]
    context = {
        'title': 'Recruiting',
        'listings': listings,
    }
    return render(request, 'recruiting/index.html', context)