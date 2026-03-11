from rest_framework import mixins, viewsets

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
  """
  POST /api/sales/
  Creates a sale with nested items, updates inventory, and computes profit.
  """

  queryset = Sale.objects.all().order_by("-created_at")
  serializer_class = SaleSerializer
