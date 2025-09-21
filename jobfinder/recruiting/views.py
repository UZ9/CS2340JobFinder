from django.shortcuts import render
from recruiting.models import Listing
from .forms import ListingForm
from django.shortcuts import redirect


def index(request):
    """Recruiting index view: show active job listings; supports simple title search via ?q=..."""
    q = request.GET.get('q', '').strip()
    qs = Listing.objects.filter(is_active=True)
    if q:
        qs = qs.filter(title__icontains=q)

    sort = request.GET.get('sort', '-posted_date')
    # allow only specific sort values to avoid misuse
    if sort == 'title':
        ordering = 'title'
    elif sort == 'location':
        ordering = 'location'
    else:
        # default to newest first
        ordering = '-posted_date'

    listings = qs.order_by(ordering)[:20]

    context = {
        'title': 'Recruiting',
        'listings': listings,
        'q': q,
    }
    return render(request, 'recruiting/index.html', context)


def create(request):
    """Create a new Listing via a simple form."""
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('recruiting.index')
    else:
        form = ListingForm()

    return render(request, 'recruiting/create.html', {'form': form, 'title': 'Create Listing'})