from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from analytics.views import AnalyticsViewSet, DashboardViewSet
from inventory.views import InventoryViewSet, StockHistoryViewSet
from products.views import CategoryViewSet, ProductViewSet
from sales.views import SaleViewSet
from store.views import (
    StoreSettingsView, 
    MeView, 
    ChangePasswordView,
    PrinterSettingsView,
    HelpInfoView,
    ActivityLogViewSet, 
    BackupView, 
    SyncView
)

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
router.register(r"dashboard", DashboardViewSet, basename="dashboard")
router.register(r"activity", ActivityLogViewSet, basename="activity")

urlpatterns = router.urls + [
    path("auth/login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("accounts/", include("accounts.api_urls")),
    path("store/", StoreSettingsView.as_view(), name="store-settings"),
    path("printer-settings/", PrinterSettingsView.as_view(), name="printer-settings"),
    path("help/", HelpInfoView.as_view(), name="help"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("backup/", BackupView.as_view(), name="backup"),
    path("sync/", SyncView.as_view(), name="sync"),
]
