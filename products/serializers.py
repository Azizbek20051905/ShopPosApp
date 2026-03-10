from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
  class Meta:
    model = Category
    fields = ["id", "name", "created_at"]
    read_only_fields = ["id", "created_at"]


class ProductSerializer(serializers.ModelSerializer):
  category = CategorySerializer(read_only=True)
  category_id = serializers.PrimaryKeyRelatedField(
    source="category",
    queryset=Category.objects.all(),
    write_only=True,
  )

  class Meta:
    model = Product
    fields = [
      "id",
      "name",
      "barcode",
      "category",
      "category_id",
      "purchase_price",
      "sale_price",
      "unit",
      "stock_quantity",
      "min_stock",
      "image",
      "created_at",
      "updated_at",
    ]
    read_only_fields = ["id", "created_at", "updated_at"]

