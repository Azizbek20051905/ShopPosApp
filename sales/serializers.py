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
  price = serializers.DecimalField(
    source="price_at_sale",
    max_digits=10,
    decimal_places=2,
    read_only=True,
  )

  class Meta:
    model = SaleItem
    fields = [
      "id",
      "product",
      "product_name",
      "quantity",
      "price",
      "price_at_sale",
      "profit",
    ]
    read_only_fields = ["id", "product_name", "price", "price_at_sale", "profit"]


class SaleSerializer(serializers.ModelSerializer):
  items = serializers.SerializerMethodField()
  created_at = serializers.DateTimeField(read_only=True)
  total_price = serializers.DecimalField(
    source="total_amount",
    max_digits=10,
    decimal_places=2,
    read_only=True,
  )
  sale_id = serializers.IntegerField(source="id", read_only=True)
  cashier_name = serializers.CharField(source="cashier.username", read_only=True)

  class Meta:
    model = Sale
    fields = [
      "id", 
      "sale_id", 
      "total_amount", 
      "total_price", 
      "total_profit", 
      "created_at", 
      "cashier", 
      "cashier_name",
      "items"
    ]
    read_only_fields = [
      "id", 
      "sale_id", 
      "total_amount", 
      "total_price", 
      "total_profit", 
      "created_at", 
      "cashier",
      "cashier_name"
    ]

  def get_items(self, obj):
    # Use the detailed serializer for retrieval
    return SaleItemSerializer(obj.items.all(), many=True).data

  def validate(self, data):
    # Handle the 'items' for POST requests manually since we use SerializerMethodField for retrieval
    items_data = self.context['request'].data.get('items', [])
    if not items_data and self.context['request'].method == 'POST':
        raise serializers.ValidationError({"items": "At least one item is required."})
    return data

  def create(self, validated_data):
    request = self.context.get("request")
    cashier = request.user if request and request.user.is_authenticated else None
    
    # Extract items directly from request data as we used SerializerMethodField for reading
    items_input_serializer = SaleItemInputSerializer(
        data=request.data.get("items", []), 
        many=True
    )
    items_input_serializer.is_valid(raise_exception=True)
    items_data = items_input_serializer.validated_data

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

      # Check for sufficient stock before proceeding
      if product.stock_quantity < qty:
        raise serializers.ValidationError({
          "items": f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {qty}"
        })

      product_updates[product.id] = product_updates.get(product.id, Decimal("0")) + qty

    with transaction.atomic():
      sale = Sale.objects.create(
        cashier=cashier,
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

