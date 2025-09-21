from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='recruiting.index'),
    path('create/', views.create, name='recruiting.create'),
]