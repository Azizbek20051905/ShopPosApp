from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from store.models import ActivityLog

from .models import StockHistory
from .serializers import AddStockSerializer, StockHistorySerializer


class InventoryViewSet(viewsets.ViewSet):
  """
  Inventory operations.
  """

  @action(detail=False, methods=["post"], url_path="add-stock")
  def add_stock(self, request):
    """
    POST /api/inventory/add-stock/
    {
      "product_id": 5,
      "quantity": 10
    }
    """
    serializer = AddStockSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()
    
    # Log the activity
    ActivityLog.objects.create(
        user=self.request.user,
        action='stock_update',
        detail=f"Stock for '{product.name}' increased by {serializer.validated_data['quantity']}."
    )
    
    return Response(
      {
        "product_id": product.id,
        "stock_quantity": str(product.stock_quantity),
      },
      status=status.HTTP_200_OK,
    )

class StockHistoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
  """
  GET /api/inventory/history/
  GET /api/inventory/history/?product=5
  """

  serializer_class = StockHistorySerializer

  def get_queryset(self):
    queryset = StockHistory.objects.select_related("product").all().order_by("-created_at")
    product_id = self.request.query_params.get("product")
    if product_id:
      queryset = queryset.filter(product_id=product_id)
    return queryset
