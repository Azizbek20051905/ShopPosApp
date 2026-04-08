from django.db import models
from tenants.models import TenantAwareModel


class DailySales(TenantAwareModel):
  date = models.DateField()
  total_sales = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0,
  )
  total_profit = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0,
  )

  class Meta:
    unique_together = ("date", "tenant")
    verbose_name = "Daily sales"
    verbose_name_plural = "Daily sales"
    ordering = ["-date"]

  def __str__(self) -> str:
    return f"{self.date:%Y-%m-%d} - {self.total_sales}"
