from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import AddStockSerializer


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
    return Response(
      {
        "product_id": product.id,
        "stock_quantity": str(product.stock_quantity),
      },
      status=status.HTTP_200_OK,
    )
