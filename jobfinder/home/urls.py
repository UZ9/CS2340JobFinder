from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home_page, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
]