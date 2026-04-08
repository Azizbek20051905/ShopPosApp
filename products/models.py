from django.db import models
from tenants.models import TenantAwareModel


class Category(TenantAwareModel):
  name = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Category"
    verbose_name_plural = "Categories"
    ordering = ["name"]

  def __str__(self) -> str:
    return self.name


class ProductType(models.TextChoices):
  PIECE = "piece", "Piece"
  WEIGHT = "weight", "Weight"


class Product(TenantAwareModel):
  name = models.CharField(max_length=150)
  barcode = models.CharField(max_length=64, null=True, blank=True)
  category = models.ForeignKey(
    Category,
    related_name="products",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
  )
  purchase_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  sale_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  type = models.CharField(
    max_length=10,
    choices=ProductType.choices,
    default=ProductType.PIECE,
  )
  # supports fractional quantities for weighted products
  stock_quantity = models.DecimalField(
    max_digits=10,
    decimal_places=3,
    default=0,
  )
  min_stock = models.DecimalField(
    max_digits=10,
    decimal_places=3,
    default=10.0,
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
