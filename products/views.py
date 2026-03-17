from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from store.models import ActivityLog


class CategoryViewSet(viewsets.ModelViewSet):
  queryset = Category.objects.all().order_by("name")
  serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
  queryset = Product.objects.select_related("category").all().order_by("name")
  serializer_class = ProductSerializer

  def perform_create(self, serializer):
      product = serializer.save()
      ActivityLog.objects.create(
          user=self.request.user,
          action='product_add',
          detail=f"Product '{product.name}' added."
      )

  def perform_update(self, serializer):
      product = serializer.save()
      ActivityLog.objects.create(
          user=self.request.user,
          action='product_update',
          detail=f"Product '{product.name}' updated."
      )

  @action(
    detail=False,
    methods=["get"],
    url_path=r"barcode/(?P<barcode>[^/]+)",
  )
  def barcode(self, request, barcode: str | None = None):
    """
    GET /api/products/barcode/{barcode}/
    """
    if not barcode:
      return Response(
        {"detail": "Barcode is required."},
        status=status.HTTP_400_BAD_REQUEST,
      )

    product = (
      Product.objects.select_related("category")
      .filter(barcode=barcode)
      .first()
    )
    if not product:
      return Response(
        {"detail": "Product not found."},
        status=status.HTTP_404_NOT_FOUND,
      )

    serializer = self.get_serializer(product)
    return Response(serializer.data)
