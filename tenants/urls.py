from django.urls import path
from .views import TenantRegistrationView

urlpatterns = [
    path('register/', TenantRegistrationView.as_view(), name='tenant-register'),
]
