from rest_framework import mixins, viewsets

from .models import Sale
from .serializers import SaleSerializer
from store.models import ActivityLog
from tenants.utils import TenantViewSetMixin


from accounts.permissions import HasStaffPermission

class SaleViewSet(
    TenantViewSetMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
  queryset = Sale.objects.select_related("cashier").prefetch_related("items__product").order_by("-created_at")
  serializer_class = SaleSerializer
  permission_classes = [HasStaffPermission]
  permission_map = {
      'list': 'can_use_pos',
      'retrieve': 'can_use_pos',
      'create': 'can_make_sale',
  }

  def perform_create(self, serializer):
      # TenantViewSetMixin handles adding the tenant
      tenant = self.request.user.profile.tenant
      sale = serializer.save(tenant=tenant)
      ActivityLog.objects.create(
          tenant=tenant,
          user=self.request.user,
          action='sale',
          detail=f"Sale #{sale.id} created. Total: {sale.total_amount} UZS"
      )
