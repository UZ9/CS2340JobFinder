from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import UserProfile, RecruiterProfile, JobSeekerProfile


def login_view(request):
    user_type = request.GET.get('user_type', 'job_seeker')

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Authenticate using email as username
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if user has the correct user type
                try:
                    profile = UserProfile.objects.get(user=user)
                    if profile.user_type == user_type:
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.email}!')
                        return redirect('home:dashboard')  # We'll create this later
                    else:
                        messages.error(request, 'Invalid user type for this account.')
                except UserProfile.DoesNotExist:
                    messages.error(request, 'User profile not found.')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()

    context = {
        'form': form,
        'user_type': user_type,
        'user_type_display': 'Recruiter' if user_type == 'recruiter' else 'Job Seeker'
    }
    return render(request, 'authentication/login.html', context)


def signup_view(request):
    user_type = request.GET.get('user_type', 'job_seeker')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create specific profile based on user type
            user_profile = UserProfile.objects.get(user=user)
            if user_type == 'recruiter':
                RecruiterProfile.objects.create(user_profile=user_profile)
            else:
                JobSeekerProfile.objects.create(user_profile=user_profile)

            messages.success(request, 'Account created successfully! Please log in.')
            return redirect(f"{reverse('authentication:login')}?user_type={user_type}")
    else:
        # Pre-fill user_type in form
        form = CustomUserCreationForm(initial={'user_type': user_type})

    context = {
        'form': form,
        'user_type': user_type,
        'user_type_display': 'Recruiter' if user_type == 'recruiter' else 'Job Seeker'
    }
    return render(request, 'authentication/signup.html', context)


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
        # Clear browser cache to prevent back button access
        response = redirect('home:index')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    else:
        # If someone tries to access logout via GET, redirect to home
        return redirect('home:index')
