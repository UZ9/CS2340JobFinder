from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .forms import ProfileForm, PrivacySettingsForm
from .models import Profile
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
                return redirect('view_profile')
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
        return redirect('create_profile')
    
    if request.method == 'POST':
        form = PrivacySettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy settings updated successfully! Recruiters will now see only the information you have enabled.')
            return redirect('view_profile')
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
        return redirect('create_profile')
    
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
    
    return render(request, 'profiles/view_profile_public.html', {
        'profile': profile,
        'visible_fields': visible_fields,
        'is_public_view': True
    })