from rest_framework import mixins, viewsets, permissions

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
  """
  POST /api/sales/ - Creates a sale.
  GET /api/sales/ - Lists sales history.
  GET /api/sales/{id}/ - Retrieves a detailed receipt.
  """
  permission_classes = [permissions.IsAuthenticated]
  queryset = (
    Sale.objects.all()
    .select_related("cashier")
    .prefetch_related("items__product")
    .order_by("-created_at")
  )
  serializer_class = SaleSerializer
