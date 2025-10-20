from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import Profile, SavedSearch, SearchNotification


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


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'show_location', 'show_skills')
    search_fields = ('user__username', 'headline', 'skills', 'location')
    actions = [export_profiles_csv]


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'recruiter', 'notification_enabled', 'created_at')
    search_fields = ('name', 'recruiter__user__username')
    actions = [export_savedsearches_csv]


@admin.register(SearchNotification)
class SearchNotificationAdmin(admin.ModelAdmin):
    list_display = ('saved_search', 'candidate', 'notified_at')
    list_filter = ('notified_at',)
    search_fields = ('saved_search__name', 'candidate__username', 'candidate__email')
    readonly_fields = ('notified_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('saved_search', 'candidate')
