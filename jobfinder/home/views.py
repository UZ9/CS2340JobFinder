from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home_page(request):
    """Main landing page where users choose between recruiter and job seeker"""

    # redirect to dashboard if already logged in 
    if request.user.is_authenticated:
        return redirect("/dashboard")

    return render(request, 'home/index.html')


@login_required
def dashboard(request):
    """Dashboard page for authenticated users"""
    return render(request, 'home/dashboard.html')


def user_type_selection(request):
    """Page to select user type before login/signup"""
    return render(request, 'home/user_type_selection.html')
