from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from profiles.models import Profile
from authentication.models import UserProfile


def home_page(request):
    """Main landing page where users choose between recruiter and job seeker"""

    # redirect to dashboard if already logged in
    if request.user.is_authenticated:
        return redirect("/dashboard")

    return render(request, 'home/index.html')


@login_required
def dashboard(request):
    """Dashboard page for authenticated users"""
    profile = None
    visible_fields = None
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        visible_fields = profile.get_visible_fields()

    context = {
        'profile': profile,
        'visible_fields': visible_fields
    }
    return render(request, 'home/dashboard.html', context)


def user_type_selection(request):
    """Page to select user type before login/signup"""
    return render(request, 'home/user_type_selection.html')


@login_required
def search_candidates(request):
    """Search page for recruiters to find candidates"""
    # Check if user is a recruiter
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, 'Only recruiters can access candidate search.')
            return redirect('home:dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
        return redirect('home:dashboard')

    # Get search parameters
    search_query = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    skills = request.GET.get('skills', '').strip()
    projects = request.GET.get('projects', '').strip()

    # Start with all profiles of job seekers
    candidates = Profile.objects.select_related('user').all()

    # Filter to only show job seeker profiles
    job_seeker_users = UserProfile.objects.filter(user_type='job_seeker').values_list('user_id', flat=True)
    candidates = candidates.filter(user_id__in=job_seeker_users)

    # Track if any search criteria was provided
    has_search_criteria = bool(search_query or location or skills or projects)

    # Apply filters based on search criteria
    if search_query:
        # General search across multiple fields
        candidates = candidates.filter(
            Q(headline__icontains=search_query) |
            Q(skills__icontains=search_query) |
            Q(work_experience__icontains=search_query) |
            Q(education__icontains=search_query) |
            Q(projects__icontains=search_query)
        )

    if location:
        candidates = candidates.filter(location__icontains=location)

    # Process skills filter and track matches
    skill_list = []
    if skills:
        # Split skills by comma and search for each
        skill_list = [s.strip().lower() for s in skills.split(',') if s.strip()]
        skill_query = Q()
        for skill in skill_list:
            skill_query |= Q(skills__icontains=skill)
        candidates = candidates.filter(skill_query)

    if projects:
        candidates = candidates.filter(projects__icontains=projects)

    # Order by most recently updated
    candidates = candidates.order_by('-updated_at')

    # Prepare candidate data with visible fields only
    candidate_list = []
    for candidate in candidates:
        visible_fields = candidate.get_visible_fields()
        if visible_fields:  # Only show candidates who have at least one visible field
            # Calculate skill match count if skills were searched
            skill_match_count = 0
            if skill_list and candidate.skills:
                candidate_skills_lower = candidate.skills.lower()
                for skill in skill_list:
                    if skill in candidate_skills_lower:
                        skill_match_count += 1

            candidate_data = {
                'user': candidate.user,
                'visible_fields': visible_fields,
                'profile': candidate,
                'skill_match_count': skill_match_count
            }
            candidate_list.append(candidate_data)

    # Sort by skill matches if skills were searched (most matches first)
    if skill_list:
        candidate_list.sort(key=lambda x: x['skill_match_count'], reverse=True)

    context = {
        'candidates': candidate_list,
        'search_query': search_query,
        'location': location,
        'skills': skills,
        'projects': projects,
        'total_results': len(candidate_list)
    }

    return render(request, 'home/search_candidates.html', context)
