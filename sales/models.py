from django.conf import settings
from django.db import models


class Sale(models.Model):
  cashier = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    related_name="sales",
    on_delete=models.PROTECT,
  )
  total_amount = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  total_profit = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Sale"
    verbose_name_plural = "Sales"
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return f"Sale #{self.pk} - {self.created_at:%Y-%m-%d %H:%M}"


class SaleItem(models.Model):
  sale = models.ForeignKey(
    Sale,
    related_name="items",
    on_delete=models.CASCADE,
  )
  product = models.ForeignKey(
    "products.Product",
    related_name="sale_items",
    on_delete=models.PROTECT,
  )
  # supports fractional quantities for weighted products
  quantity = models.DecimalField(
    max_digits=10,
    decimal_places=3,
  )
  price_at_sale = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )
  profit = models.DecimalField(
    max_digits=10,
    decimal_places=2,
  )

  class Meta:
    verbose_name = "Sale item"
    verbose_name_plural = "Sale items"

  def __str__(self) -> str:
    return f"{self.product} x {self.quantity}"
