from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import ProfileForm, PrivacySettingsForm
from .models import Profile
import re
from django.db.models import Q
from django.utils import timezone
from .forms import ProfileForm, PrivacySettingsForm, SavedSearchForm, CandidateSearchForm
from .models import Profile, SavedSearch, SearchNotification
from authentication.models import RecruiterProfile, UserProfile
# Create your views here.

@login_required
def create_profile(request):
    try:
        profile = request.user.profile
        is_edit = True
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        is_edit = False
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            try:
                form.save()
                action = 'updated' if is_edit else 'created'
                messages.success(request, f'Profile {action} successfully! Recruiters can now see your information based on your privacy settings.')
                return redirect('home:dashboard')
            except ValidationError as e:
                messages.error(request, f'Error saving profile: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profiles/create_profile.html', {
        'form': form, 
        'is_edit': is_edit,
        'profile': profile
    })

@login_required
def privacy_settings(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.warning(request, 'Please create your profile first before setting privacy options.')
        return redirect('profiles:create_profile')
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings updated successfully! Recruiters will now see only the information you have enabled.')
            return redirect('home:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PrivacySettingsForm(instance=profile)
    
    return render(request, 'profiles/privacy_settings.html', {
        'form': form,
        'profile': profile
    })

@login_required
def view_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.info(request, 'Please create your profile to get started.')
        return redirect('profiles:create_profile')
    
    # Get visible fields for recruiter view
    visible_fields = profile.get_visible_fields()
    
    return render(request, 'profiles/view_profile.html', {
        'profile': profile,
        'visible_fields': visible_fields
    })

def view_profile_public(request, user_id):
    """Public view of profile for recruiters - only shows fields marked as visible"""
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        profile = user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, 'Profile not found.')
        return redirect('home')  # You'll need to create a home view
    
    # Only show fields that are marked as visible to recruiters
    visible_fields = profile.get_visible_fields()

    # Preprocess certain fields for template convenience (e.g., split links into a list)
    processed = {}
    for fname, fval in visible_fields.items():
        if fname == 'links' and fval:
            # split on newlines, commas, or semicolons
            links = [l.strip() for l in re.split(r"[\n\r,;]+", fval) if l.strip()]
            processed[fname] = links
        else:
            processed[fname] = fval

    return render(request, 'profiles/view_profile_public.html', {
        'profile': profile,
        'visible_fields': processed,
        'is_public_view': True
    })


# Saved Search Views (for Recruiters)

def _check_recruiter_access(request):
    """Helper function to check if user is a recruiter"""
    try:
        user_profile = request.user.userprofile
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'This feature is only available to recruiters.')
            return None
        return user_profile.recruiterprofile
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, 'Recruiter profile not found.')
        return None


@login_required
def saved_searches_list(request):
    """List all saved searches for the current recruiter"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    saved_searches = recruiter_profile.saved_searches.all()
    
    return render(request, 'profiles/saved_searches_list.html', {
        'saved_searches': saved_searches
    })


@login_required
def create_saved_search(request):
    """Create a new saved search"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    if request.method == 'POST':
        form = SavedSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.recruiter = recruiter_profile
            saved_search.save()
            messages.success(request, f'Saved search "{saved_search.name}" created successfully!')
            return redirect('profiles:saved_searches_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SavedSearchForm()
    
    return render(request, 'profiles/saved_search_form.html', {
        'form': form,
        'is_edit': False
    })


@login_required
def edit_saved_search(request, search_id):
    """Edit an existing saved search"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    saved_search = get_object_or_404(SavedSearch, id=search_id, recruiter=recruiter_profile)
    
    if request.method == 'POST':
        form = SavedSearchForm(request.POST, instance=saved_search)
        if form.is_valid():
            form.save()
            messages.success(request, f'Saved search "{saved_search.name}" updated successfully!')
            return redirect('profiles:saved_searches_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SavedSearchForm(instance=saved_search)
    
    return render(request, 'profiles/saved_search_form.html', {
        'form': form,
        'is_edit': True,
        'saved_search': saved_search
    })


@login_required
def delete_saved_search(request, search_id):
    """Delete a saved search"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    saved_search = get_object_or_404(SavedSearch, id=search_id, recruiter=recruiter_profile)
    
    if request.method == 'POST':
        search_name = saved_search.name
        saved_search.delete()
        messages.success(request, f'Saved search "{search_name}" deleted successfully!')
        return redirect('profiles:saved_searches_list')
    
    return render(request, 'profiles/saved_search_confirm_delete.html', {
        'saved_search': saved_search
    })


@login_required
def execute_saved_search(request, search_id):
    """Execute a saved search and show results"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    saved_search = get_object_or_404(SavedSearch, id=search_id, recruiter=recruiter_profile)
    candidates = saved_search.execute_search()
    
    return render(request, 'profiles/search_results.html', {
        'saved_search': saved_search,
        'candidates': candidates,
        'is_saved_search': True
    })


@login_required
def search_candidates(request):
    """Quick search for candidates without saving"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    candidates = None
    form = CandidateSearchForm()
    
    if request.method == 'GET' and any(request.GET.values()):
        form = CandidateSearchForm(request.GET)
        if form.is_valid():
            # Build query
            search_query = form.cleaned_data.get('search_query', '').strip()
            location = form.cleaned_data.get('location', '').strip()
            skills = form.cleaned_data.get('skills', '').strip()
            
            # Start with all job seeker profiles
            candidates = Profile.objects.filter(
                user__userprofile__user_type='job_seeker'
            )
            
            # Apply filters
            if search_query:
                query = Q()
                search_terms = search_query.lower().split()
                for term in search_terms:
                    query |= Q(headline__icontains=term)
                    query |= Q(skills__icontains=term)
                    query |= Q(education__icontains=term)
                    query |= Q(work_experience__icontains=term)
                    query |= Q(projects__icontains=term)
                candidates = candidates.filter(query)
            
            if location:
                candidates = candidates.filter(
                    location__icontains=location,
                    show_location=True
                )
            
            if skills:
                skill_list = [s.strip() for s in skills.split(',') if s.strip()]
                skill_query = Q()
                for skill in skill_list:
                    skill_query |= Q(skills__icontains=skill)
                candidates = candidates.filter(skill_query, show_skills=True)
            
            candidates = candidates.distinct()
    
    return render(request, 'profiles/search_candidates.html', {
        'form': form,
        'candidates': candidates
    })


@login_required
def saved_search_notifications(request):
    """View notifications for new candidate matches"""
    recruiter_profile = _check_recruiter_access(request)
    if not recruiter_profile:
        return redirect('home:dashboard')
    
    # Get all saved searches with notifications enabled
    saved_searches = recruiter_profile.saved_searches.filter(notification_enabled=True)
    
    # Get recent notifications
    recent_notifications = SearchNotification.objects.filter(
        saved_search__recruiter=recruiter_profile
    ).select_related('saved_search', 'candidate', 'candidate__profile')[:50]
    
    return render(request, 'profiles/saved_search_notifications.html', {
        'saved_searches': saved_searches,
        'recent_notifications': recent_notifications
    })
