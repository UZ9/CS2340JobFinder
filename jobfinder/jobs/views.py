from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from authentication.models import UserProfile, RecruiterProfile, JobSeekerProfile
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm


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
    
    # Pagination
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
