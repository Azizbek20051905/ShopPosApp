from django.urls import path
from .views import landing_view, auth_view, pos_view, billing_view

urlpatterns = [
    path('', landing_view, name='landing'),
    path('login/', auth_view, name='login'),
    path('register/', auth_view, name='register'),
    path('dashboard/', pos_view, name='pos-dashboard'),
    path('billing/', billing_view, name='billing'),
]
