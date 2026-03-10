from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginAPIView, UserDetailView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('me/', UserDetailView.as_view(), name='user-me'),
    path('', include(router.urls)),
]

