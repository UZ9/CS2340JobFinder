from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('create/', views.create_profile, name='create_profile'),
    path('privacy/', views.privacy_settings, name='privacy_settings'),
    path('view/', views.view_profile, name='view_profile'),
    path('public/<int:user_id>/', views.view_profile_public, name='view_profile_public'),
]