from django.db import models


class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"
    ordering = ["name"]

  def __str__(self) -> str:
    return self.name


class ProductUnit(models.TextChoices):
  PIECE = "piece", "Piece"
  KG = "kg", "Kg"


class Product(models.Model):
  name = models.CharField(max_length=150)
  barcode = models.CharField(max_length=64, unique=True)
  category = models.ForeignKey(
    Category,
    related_name="products",
    on_delete=models.PROTECT,
  )
  purchase_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  sale_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  unit = models.CharField(
    max_length=10,
    choices=ProductUnit.choices,
    default=ProductUnit.PIECE,
  )
  # supports fractional quantities for weighted products
  stock_quantity = models.DecimalField(
    max_digits=10,
    decimal_places=3,
    default=0,
  )
  image = models.ImageField(
    upload_to="products/",
    blank=True,
    null=True,
  )
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    verbose_name = "Product"
    verbose_name_plural = "Products"
    ordering = ["name"]

  def __str__(self) -> str:
    return f"{self.name} ({self.barcode})"
