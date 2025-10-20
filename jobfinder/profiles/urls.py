from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'profiles'

urlpatterns = [
    path('create/', views.create_profile, name='create_profile'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
    path('view/', views.view_profile, name='view_profile'),
    path('public/<int:user_id>/', views.view_profile_public, name='view_profile_public'),
    
    # Candidate search
    path('search/', views.search_candidates, name='search_candidates'),
    
    # Saved searches
    path('saved-searches/', views.saved_searches_list, name='saved_searches_list'),
    path('saved-searches/create/', views.create_saved_search, name='create_saved_search'),
    path('saved-searches/<int:search_id>/edit/', views.edit_saved_search, name='edit_saved_search'),
    path('saved-searches/<int:search_id>/delete/', views.delete_saved_search, name='delete_saved_search'),
    path('saved-searches/<int:search_id>/execute/', views.execute_saved_search, name='execute_saved_search'),
    
    # Notifications
    path('saved-searches/notifications/', views.saved_search_notifications, name='saved_search_notifications'),
    path('saved-searches/help/', lambda request: render(request, 'profiles/saved_search_help.html'), name='saved_search_help'),
]
