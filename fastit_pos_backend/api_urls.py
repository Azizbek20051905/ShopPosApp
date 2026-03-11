from rest_framework.routers import DefaultRouter

from analytics.views import AnalyticsViewSet
from inventory.views import InventoryViewSet
from products.views import CategoryViewSet, ProductViewSet
from sales.views import SaleViewSet

router = DefaultRouter()

# API structure:
# /api/products/
# /api/categories/
# /api/sales/
# /api/inventory/
# /api/analytics/
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"sales", SaleViewSet, basename="sale")
router.register(r"inventory", InventoryViewSet, basename="inventory")
router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = router.urls

