from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from inventory.models import StockHistory, StockHistoryType
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

    with transaction.atomic():
      # Lock all products involved to prevent race conditions.
      product_ids = [item["product"].id for item in items_data]
      locked_products = (
        Product.objects.select_for_update()
        .filter(id__in=product_ids)
      )
      product_by_id = {p.id: p for p in locked_products}

      # Aggregate quantities per product (barcode scans can add same product multiple times).
      requested_qty: dict[int, Decimal] = {}
      for item in items_data:
        product: Product = item["product"]
        qty: Decimal = item["quantity"]
        requested_qty[product.id] = requested_qty.get(product.id, Decimal("0")) + qty

      # Validate stock before any write.
      errors: list[dict[str, str]] = []
      for pid, qty in requested_qty.items():
        product = product_by_id.get(pid)
        if product is None:
          errors.append({"product_id": str(pid), "detail": "Product not found."})
          continue

        if product.stock_quantity <= 0:
          errors.append(
            {
              "product_id": str(pid),
              "barcode": product.barcode,
              "detail": "Product is out of stock.",
            }
          )
        elif product.stock_quantity < qty:
          errors.append(
            {
              "product_id": str(pid),
              "barcode": product.barcode,
              "detail": "Not enough stock.",
            }
          )

      if errors:
        raise serializers.ValidationError({"items": errors})

      # Compute totals using locked rows (consistent values).
      total_amount = Decimal("0")
      total_profit = Decimal("0")
      for pid, qty in requested_qty.items():
        product = product_by_id[pid]
        total_amount += product.sale_price * qty
        total_profit += (product.sale_price - product.purchase_price) * qty

      cashier = self.context["request"].user
      sale = Sale.objects.create(total_amount=total_amount, total_profit=total_profit, cashier=cashier)

      # Create sale items (one per request entry, not aggregated) to keep payload traceable.
      for item in items_data:
        product: Product = product_by_id[item["product"].id]
        qty: Decimal = item["quantity"]
        SaleItem.objects.create(
          sale=sale,
          product=product,
          quantity=qty,
          price_at_sale=product.sale_price,
          profit=(product.sale_price - product.purchase_price) * qty,
        )

      # Decrease stock quantities and log history.
      for pid, qty in requested_qty.items():
        product = product_by_id[pid]
        product.stock_quantity = product.stock_quantity - qty
        product.save(update_fields=["stock_quantity"])

        StockHistory.objects.create(
          product=product,
          change_amount=-qty,
          type=StockHistoryType.SALE,
        )

    return sale

