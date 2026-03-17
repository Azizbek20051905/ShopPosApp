from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product
from .models import StockHistory, StockHistoryType


class AddStockSerializer(serializers.Serializer):
  product_id = serializers.PrimaryKeyRelatedField(
    queryset=Product.objects.all(),
    source="product",
  )
  quantity = serializers.DecimalField(
    max_digits=10,
    decimal_places=3,
    min_value=Decimal("0.001"),
  )

  def create(self, validated_data):
    product: Product = validated_data["product"]
    qty: Decimal = validated_data["quantity"]

    with transaction.atomic():
      product = Product.objects.select_for_update().get(id=product.id)
      product.stock_quantity = product.stock_quantity + qty
      product.save(update_fields=["stock_quantity"])

      StockHistory.objects.create(
        product=product,
        change_amount=qty,
        type=StockHistoryType.ADD,
      )

    return product


class StockHistorySerializer(serializers.ModelSerializer):
  product_name = serializers.CharField(source="product.name", read_only=True)

  class Meta:
    model = StockHistory
    fields = ["id", "product", "product_name", "change_amount", "type", "created_at"]
    read_only_fields = fields
