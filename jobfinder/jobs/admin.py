from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'work_type', 'experience_level', 'visa_sponsorship', 'created_at', 'is_active']
    list_filter = ['work_type', 'experience_level', 'visa_sponsorship', 'is_active', 'created_at']
    search_fields = ['title', 'company', 'skills_required', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['applicant__username', 'job__title', 'job__company']
    ordering = ['-applied_at']
    readonly_fields = ['applied_at', 'updated_at']
