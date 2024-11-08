from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list, name='request_list'),  # List all requests
    path('create/', views.create_request, name='create_request'),
    path('<uuid:request_id>/', views.request_detail, name='request_detail'),
    path('<uuid:request_id>/update-status/', views.update_request_status, name='update_request_status'),
    path('<uuid:request_id>/edit/', views.edit_request, name='edit_request'),
]
