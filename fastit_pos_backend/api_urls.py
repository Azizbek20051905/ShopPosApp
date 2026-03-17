from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from analytics.views import AnalyticsViewSet
from inventory.views import InventoryViewSet, StockHistoryViewSet
from products.views import CategoryViewSet, ProductViewSet
from sales.views import SaleViewSet

router = DefaultRouter()

# API structure:
# /api/products/
# /api/categories/
# /api/sales/
# /api/inventory/
# /api/analytics/
# /api/accounts/users/
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"inventory/history", StockHistoryViewSet, basename="inventory-history")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = router.urls + [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/", include("accounts.api_urls")),
]
