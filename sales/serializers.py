from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from products.models import Product
from .models import Sale, SaleItem


class SaleItemInputSerializer(serializers.Serializer):
  product_id = serializers.PrimaryKeyRelatedField(
    queryset=Product.objects.all(),
    source="product",
  )
  quantity = serializers.DecimalField(
    max_digits=10,
    decimal_places=3,
    min_value=Decimal("0.001"),
  )


class SaleItemSerializer(serializers.ModelSerializer):
  product_name = serializers.CharField(source="product.name", read_only=True)

  class Meta:
    model = SaleItem
    fields = [
      "id",
      "product",
      "product_name",
      "quantity",
      "price_at_sale",
      "profit",
    ]
    read_only_fields = ["id", "product_name", "price_at_sale", "profit"]


class SaleSerializer(serializers.ModelSerializer):
  items = SaleItemInputSerializer(many=True, write_only=True)
  created_at = serializers.DateTimeField(read_only=True)

  class Meta:
    model = Sale
    fields = ["id", "total_amount", "total_profit", "created_at", "items"]
    read_only_fields = ["id", "total_amount", "total_profit", "created_at"]

  def create(self, validated_data):
    items_data = validated_data.pop("items", [])
    if not items_data:
      raise serializers.ValidationError({"items": "At least one item is required."})

    total_amount = Decimal("0")
    total_profit = Decimal("0")

    product_updates: dict[int, Decimal] = {}

    for item in items_data:
      product: Product = item["product"]
      qty: Decimal = item["quantity"]

      line_total = product.sale_price * qty
      line_profit = (product.sale_price - product.purchase_price) * qty

      total_amount += line_total
      total_profit += line_profit

      product_updates[product.id] = product_updates.get(product.id, Decimal("0")) + qty

    with transaction.atomic():
      sale = Sale.objects.create(
        total_amount=total_amount,
        total_profit=total_profit,
      )

      for item in items_data:
        product: Product = item["product"]
        qty: Decimal = item["quantity"]
        SaleItem.objects.create(
          sale=sale,
          product=product,
          quantity=qty,
          price_at_sale=product.sale_price,
          profit=(product.sale_price - product.purchase_price) * qty,
        )

      # update stock quantities
      for product_id, qty in product_updates.items():
        product = Product.objects.select_for_update().get(id=product_id)
        product.stock_quantity = product.stock_quantity - qty
        product.save(update_fields=["stock_quantity"])

    return sale

