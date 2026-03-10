from django.urls import path, include

urlpatterns = [
    path('', include('accounts.api_urls')), # Handles /api/login/, /api/users/, etc.
    path('', include('products.api_urls')),
    path('sales/', include('sales.api_urls')),
    path('inventory/', include('inventory.api_urls')),
    path('analytics/', include('analytics.api_urls')),
]

