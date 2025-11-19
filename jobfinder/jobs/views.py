from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from authentication.models import UserProfile, RecruiterProfile, JobSeekerProfile
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
import re
import math


def job_list(request):
    """Main jobs page with search and filtering"""
    jobs = Job.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(skills_required__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by location
    location = request.GET.get('location', '')
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    # Filter by work type
    work_type = request.GET.get('work_type', '')
    if work_type:
        jobs = jobs.filter(work_type=work_type)
    
    # Filter by visa sponsorship
    visa_sponsorship = request.GET.get('visa_sponsorship', '')
    if visa_sponsorship == 'true':
        jobs = jobs.filter(visa_sponsorship=True)
    
    # Filter by salary range
    salary_min = request.GET.get('salary_min', '')
    salary_max = request.GET.get('salary_max', '')
    if salary_min:
        try:
            jobs = jobs.filter(salary_min__gte=int(salary_min))
        except ValueError:
            pass
    if salary_max:
        try:
            jobs = jobs.filter(salary_max__lte=int(salary_max))
        except ValueError:
            pass
    
    # Filter by experience level
    experience_level = request.GET.get('experience_level', '')
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)
    
    # --- Commute/distance filtering ---
    # The UI will provide `start_city` (string) and `commute_miles` (int) via GET.
    # We keep a small mapping of common city names -> (lat, lon). Jobs whose
    # `location` text contains a known city name will be assigned that city's
    # coordinates. If a commute filter is provided and a job's location doesn't
    # map to a known city, the job will be excluded (we can't compute distance).
    CITY_COORDS = {
        'new york': (40.7128, -74.0060),
        'san francisco': (37.7749, -122.4194),
        'los angeles': (34.0522, -118.2437),
        'chicago': (41.8781, -87.6298),
        'boston': (42.3601, -71.0589),
        'seattle': (47.6062, -122.3321),
        'austin': (30.2672, -97.7431),
        'denver': (39.7392, -104.9903),
        'atlanta': (33.7490, -84.3880),
        'portland': (45.5051, -122.6750),
        'los angeles, ca': (34.0522, -118.2437),
    }

    def haversine_miles(lat1, lon1, lat2, lon2):
        # Haversine formula to compute distance between two lat/lon in miles
        R = 3958.8  # Earth radius in miles
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def find_city_coords(text):
        if not text:
            return None
        t = text.lower()
        # try to match any city key that appears in the text
        for city, coords in CITY_COORDS.items():
            if city in t:
                return coords
        return None

    start_city = request.GET.get('start_city', '')
    commute_miles = request.GET.get('commute_miles', '')

    try:
        commute_val = float(commute_miles) if commute_miles else None
    except ValueError:
        commute_val = None

    # If start_city provided, try to resolve to coordinates
    start_coords = None
    if start_city:
        start_coords = CITY_COORDS.get(start_city.lower()) or None

    # Apply distance filtering if both start_coords and commute_val are present
    if start_coords and commute_val:
        filtered = []
        # evaluate current queryset into list
        for j in jobs:
            job_coords = find_city_coords(j.location or '')
            if not job_coords:
                # skip jobs with unknown/ambiguous locations when commute filter is active
                continue
            dist = haversine_miles(start_coords[0], start_coords[1], job_coords[0], job_coords[1])
            if dist <= commute_val:
                filtered.append(j)
        jobs = filtered

    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    # Check user type for conditional rendering
    user_type = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_type = user_profile.user_type
        except UserProfile.DoesNotExist:
            pass
    
    context = {
        'jobs': jobs_page,
        'search_query': search_query,
        'location': location,
        'work_type': work_type,
        'visa_sponsorship': visa_sponsorship,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'experience_level': experience_level,
        'user_type': user_type,
        'work_type_choices': Job.WORK_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    'recommended_jobs': recommended_jobs,
    'start_city': start_city,
    'commute_miles': commute_miles,
    'city_choices': sorted([c.title() for c in CITY_COORDS.keys()]),
    }
    
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    """Job detail page"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user has already applied (for job seekers)
    has_applied = False
    user_type = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            user_type = user_profile.user_type
            if user_type == 'job_seeker':
                has_applied = JobApplication.objects.filter(
                    job=job, applicant=request.user
                ).exists()
        except UserProfile.DoesNotExist:
            pass
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'user_type': user_type,
    }
    
    return render(request, 'jobs/job_detail.html', context)


@login_required
def my_jobs(request):
    """Recruiter's job management page"""
    # Check if user is a recruiter
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can access this page.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    jobs = Job.objects.filter(recruiter=recruiter_profile).order_by('-created_at')
    
    context = {
        'jobs': jobs,
    }
    
    return render(request, 'jobs/my_jobs.html', context)


@login_required
def add_job(request):
    """Add new job (recruiters only)"""
    # Check if user is a recruiter
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can add jobs.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = recruiter_profile
            job.save()
            messages.success(request, "Job posted successfully!")
            return redirect('jobs:my_jobs')
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'title': 'Add New Job',
    }
    
    return render(request, 'jobs/job_form.html', context)


@login_required
def edit_job(request, job_id):
    """Edit job (recruiters only, own jobs only)"""
    # Check if user is a recruiter
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can edit jobs.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect('jobs:my_jobs')
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'title': 'Edit Job',
    }
    
    return render(request, 'jobs/job_form.html', context)


@login_required
def delete_job(request, job_id):
    """Delete job (recruiters only, own jobs only)"""
    # Check if user is a recruiter
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can delete jobs.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile)
    
    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('jobs:my_jobs')
    
    context = {
        'job': job,
    }
    
    return render(request, 'jobs/job_confirm_delete.html', context)


@login_required
def apply_to_job(request, job_id):
    """Apply to job (job seekers only)"""
    # Check if user is a job seeker
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, "Only job seekers can apply to jobs.")
            return redirect('jobs:job_detail', job_id=job_id)
        
        job_seeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, "Job seeker profile not found.")
        return redirect('jobs:job_detail', job_id=job_id)
    
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied to this job.")
        return redirect('jobs:job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, "Application submitted successfully!")
            return redirect('jobs:job_detail', job_id=job_id)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    
    return render(request, 'jobs/apply_job.html', context)


@login_required
def my_applications(request):
    """Job seeker's applications page"""
    # Check if user is a job seeker
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, "Only job seekers can view applications.")
            return redirect('jobs:job_list')
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('jobs:job_list')
    
    applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')
    
    context = {
        'applications': applications,
    }
    
    return render(request, 'jobs/my_applications.html', context)


@login_required
def application_pipeline(request, job_id):
    """Kanban board view for managing job applications (recruiters only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can access the application pipeline.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile)
    
    # Get applications grouped by status
    applications_by_status = {
        'applied': job.applications.filter(status='applied').order_by('-applied_at'),
        'review': job.applications.filter(status='review').order_by('-status_updated_at'),
        'interview': job.applications.filter(status='interview').order_by('-status_updated_at'),
        'offer': job.applications.filter(status='offer').order_by('-status_updated_at'),
        'closed': job.applications.filter(status='closed').order_by('-status_updated_at'),
    }
    
    context = {
        'job': job,
        'applications_by_status': applications_by_status,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    
    return render(request, 'jobs/application_pipeline.html', context)


@login_required
def applicants_map(request, job_id):
    """Map view showing clusters of applicants by location (recruiters only)"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            messages.error(request, "Only recruiters can access the applicants map.")
            return redirect('jobs:job_list')
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, RecruiterProfile.DoesNotExist):
        messages.error(request, "Recruiter profile not found.")
        return redirect('jobs:job_list')
    
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile)
    
    context = {
        'job': job,
    }
    
    return render(request, 'jobs/applicants_map.html', context)
