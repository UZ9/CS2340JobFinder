from django.urls import path
from . import views, ajax_views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('add/', views.add_job, name='add_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('my-applications/', views.my_applications, name='my_applications'),
    
    # Application pipeline
    path('<int:job_id>/pipeline/', views.application_pipeline, name='application_pipeline'),
    
    # Applicants map
    path('<int:job_id>/applicants-map/', views.applicants_map, name='applicants_map'),
    
    # recommeded candidates
    path('<int:job_id>/recommended-candidates/', views.recommended_candidates, name='recommended_candidates'),
    
    # AJAX endpoints
    path('ajax/update-status/', ajax_views.update_application_status, name='ajax_update_status'),
    path('ajax/batch-update/', ajax_views.batch_update_status, name='ajax_batch_update'),
    path('ajax/delete-application/', ajax_views.delete_application, name='ajax_delete_application'),
    path('ajax/messages/<int:application_id>/', ajax_views.application_messages, name='ajax_messages'),
    path('ajax/send-message/', ajax_views.send_message, name='ajax_send_message'),
    path('ajax/unread-count/', ajax_views.get_unread_message_count, name='ajax_unread_count'),
    path('ajax/conversations/', ajax_views.get_conversations, name='ajax_conversations'),
    path('ajax/<int:job_id>/applicant-locations/', ajax_views.get_applicant_locations, name='ajax_applicant_locations'),
]
