from django.urls import path, include
from accounts.views import LoginAPIView, UserListView

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='users'),
    path('accounts/', include('accounts.api_urls')),
    path('', include('products.api_urls')),
    path('sales/', include('sales.api_urls')),
    path('inventory/', include('inventory.api_urls')),
    path('analytics/', include('analytics.api_urls')),
]

