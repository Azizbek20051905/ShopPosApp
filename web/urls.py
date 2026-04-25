from django.urls import path
from .views import landing_view, auth_view, dashboard_view, pos_view, manage_view, billing_view, download_view

urlpatterns = [
    path('', landing_view, name='landing'),
    path('login/', auth_view, name='login'),
    path('register/', auth_view, name='register'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('pos/', pos_view, name='pos-terminal'),
    path('manage/', manage_view, name='management'),
    path('billing/', billing_view, name='billing'),
    path('download/', download_view, name='download'),
]
