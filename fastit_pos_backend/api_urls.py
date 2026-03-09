from django.urls import path, include

urlpatterns = [
    path('accounts/', include('accounts.api_urls')),
    path('', include('products.api_urls')),
    path('sales/', include('sales.api_urls')),
    path('inventory/', include('inventory.api_urls')),
    path('analytics/', include('analytics.api_urls')),
]

