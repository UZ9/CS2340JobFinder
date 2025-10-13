from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    path('add/', views.add_job, name='add_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('<int:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('<int:job_id>/recommended-candidates/', views.recommended_candidates, name='recommended_candidates'),
    path('my-applications/', views.my_applications, name='my_applications'),
]