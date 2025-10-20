from django.contrib import admin
from .models import Profile, SavedSearch, SearchNotification


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'headline', 'location', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'show_headline', 'show_skills')
    search_fields = ('user__username', 'user__email', 'headline', 'skills', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('headline', 'skills', 'education', 'work_experience', 'links', 'location', 'projects')
        }),
        ('Privacy Settings', {
            'fields': (
                'show_headline', 'show_skills', 'show_education',
                'show_work_experience', 'show_links', 'show_location', 'show_projects'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'recruiter', 'notification_enabled', 'last_notified', 'created_at')
    list_filter = ('notification_enabled', 'created_at', 'last_notified')
    search_fields = ('name', 'recruiter__user_profile__user__username', 'search_query', 'skills', 'location')
    readonly_fields = ('created_at', 'updated_at', 'last_notified')
    
    fieldsets = (
        ('Search Information', {
            'fields': ('recruiter', 'name')
        }),
        ('Search Criteria', {
            'fields': ('search_query', 'location', 'skills', 'projects')
        }),
        ('Notifications', {
            'fields': ('notification_enabled', 'last_notified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('recruiter__user_profile__user')


@admin.register(SearchNotification)
class SearchNotificationAdmin(admin.ModelAdmin):
    list_display = ('saved_search', 'candidate', 'notified_at')
    list_filter = ('notified_at',)
    search_fields = ('saved_search__name', 'candidate__username', 'candidate__email')
    readonly_fields = ('notified_at',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('saved_search', 'candidate')
