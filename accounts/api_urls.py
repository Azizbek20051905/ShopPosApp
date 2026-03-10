from django.urls import path
from .views import LoginAPIView, UserDetailView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-me'),
]

