from django.contrib import admin
from .models import UserProfile, RecruiterProfile, JobSeekerProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__email', 'user__username']


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'company_name']
    search_fields = ['user_profile__user__email', 'company_name']


@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'experience_years', 'resume_uploaded']
    list_filter = ['experience_years', 'resume_uploaded']
    search_fields = ['user_profile__user__email']
