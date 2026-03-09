from django.db import models


class StockHistoryType(models.TextChoices):
  ADD = "add", "Add"
  SALE = "sale", "Sale"
  ADJUSTMENT = "adjustment", "Adjustment"


class StockHistory(models.Model):
  product = models.ForeignKey(
    "products.Product",
    related_name="stock_history",
    on_delete=models.CASCADE,
  )
  # positive for stock-in, negative for stock-out if desired
  change_amount = models.DecimalField(
    max_digits=10,
    decimal_places=3,
  )
  type = models.CharField(
    max_length=20,
    choices=StockHistoryType.choices,
  )
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    verbose_name = "Stock history entry"
    verbose_name_plural = "Stock history"
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return f"{self.product} {self.change_amount} ({self.type})"
