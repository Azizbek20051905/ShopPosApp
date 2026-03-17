from rest_framework import mixins, viewsets

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
  """
  POST /api/sales/
  Creates a sale with nested items, updates inventory, and computes profit.
  GET /api/sales/
  Returns a list of all sales, ordered newest first.
  GET /api/sales/<id>/
  Retrieves a strict sale containing all product-related metadata.
  """

  queryset = Sale.objects.select_related("cashier").prefetch_related("items__product").order_by("-created_at")
  serializer_class = SaleSerializer
