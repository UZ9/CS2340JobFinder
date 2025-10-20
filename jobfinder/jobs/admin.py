import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import Job, JobApplication, Message

def export_profiles_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=profiles_export.csv'
    writer = csv.writer(response)

    writer.writerow([
        'id', 'username', 'email', 'first_name', 'last_name',
        'headline', 'location', 'skills', 'links', 'created_at'
    ])

    for obj in queryset.select_related('user'):
        writer.writerow([
            obj.id,
            obj.user.username if obj.user else '',
            obj.user.email if obj.user else '',
            getattr(obj.user, 'first_name', ''),
            getattr(obj.user, 'last_name', ''),
            getattr(obj, 'headline', ''),
            getattr(obj, 'location', ''),
            getattr(obj, 'skills', ''),
            getattr(obj, 'links', ''),
            getattr(obj, 'created_at', ''),
        ])

    return response
export_profiles_csv.short_description = "Export selected profiles to CSV"


def export_savedsearches_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=savedsearches_export.csv'
    writer = csv.writer(response)

    writer.writerow([
        'id', 'name', 'recruiter_username', 'query', 'notification_enabled', 'created_at'
    ])

    for obj in queryset.select_related('recruiter__user'):
        recruiter_name = obj.recruiter.user.username if getattr(obj, 'recruiter', None) and getattr(obj.recruiter, 'user', None) else ''
        writer.writerow([
            obj.id,
            getattr(obj, 'name', ''),
            recruiter_name,
            getattr(obj, 'query', ''),
            getattr(obj, 'notification_enabled', False),
            getattr(obj, 'created_at', ''),
        ])

    return response
export_savedsearches_csv.short_description = "Export selected saved searches to CSV"



def export_jobs_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=jobs_export.csv'
    writer = csv.writer(response)
    writer.writerow([
        'id', 'title', 'company', 'location', 'work_type',
        'experience_level', 'visa_sponsorship', 'skills_required',
        'is_active', 'created_at', 'updated_at'
    ])
    for obj in queryset:
        writer.writerow([
            obj.id,
            getattr(obj, 'title', ''),
            getattr(obj, 'company', ''),
            getattr(obj, 'location', ''),
            getattr(obj, 'work_type', ''),
            getattr(obj, 'experience_level', ''),
            getattr(obj, 'visa_sponsorship', ''),
            getattr(obj, 'skills_required', ''),
            getattr(obj, 'is_active', ''),
            getattr(obj, 'created_at', ''),
            getattr(obj, 'updated_at', ''),
        ])
    return response
export_jobs_csv.short_description = "Export selected jobs to CSV"


def export_jobapplications_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=jobapplications_export.csv'
    writer = csv.writer(response)
    writer.writerow([
        'id', 'applicant_username', 'applicant_email', 'job_id', 'job_title',
        'status', 'notified', 'applied_at', 'updated_at', 'resume'
    ])
    for obj in queryset.select_related('job', 'applicant'):
        applicant_username = getattr(obj.applicant, 'username', '') if getattr(obj, 'applicant', None) else ''
        applicant_email = getattr(obj.applicant, 'email', '') if getattr(obj, 'applicant', None) else ''
        writer.writerow([
            obj.id,
            applicant_username,
            applicant_email,
            getattr(obj.job, 'id', ''),
            getattr(obj.job, 'title', ''),
            getattr(obj, 'status', ''),
            getattr(obj, 'notified', False),
            getattr(obj, 'applied_at', ''),
            getattr(obj, 'updated_at', ''),
            getattr(obj, 'resume', ''),
        ])
    return response
export_jobapplications_csv.short_description = "Export selected job applications to CSV"


def export_messages_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=messages_export.csv'
    writer = csv.writer(response)
    writer.writerow([
        'id', 'sender_username', 'application_id', 'application_applicant', 'is_read', 'content', 'created_at'
    ])
    for obj in queryset.select_related('sender', 'application', 'application__applicant'):
        sender_username = getattr(obj.sender, 'username', '') if getattr(obj, 'sender', None) else ''
        app_id = getattr(obj.application, 'id', '')
        app_applicant = getattr(getattr(obj.application, 'applicant', None), 'username', '')
        writer.writerow([
            obj.id,
            sender_username,
            app_id,
            app_applicant,

            getattr(obj, 'is_read', False),
            getattr(obj, 'content', ''),
            getattr(obj, 'created_at', ''),
        ])
    return response
export_messages_csv.short_description = "Export selected messages to CSV"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'work_type', 'experience_level', 'visa_sponsorship', 'created_at', 'is_active']
    list_filter = ['work_type', 'experience_level', 'visa_sponsorship', 'is_active', 'created_at']
    search_fields = ['title', 'company', 'skills_required', 'location']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    actions = [ export_jobs_csv ]

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'notified', 'applied_at']
    list_filter = ['status', 'notified', 'applied_at']
    search_fields = ['applicant__username', 'job__title', 'job__company']
    ordering = ['-applied_at']
    readonly_fields = ['applied_at', 'updated_at', 'status_updated_at']
    actions = [ export_jobapplications_csv ]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'application', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    actions = [ export_messages_csv ]
