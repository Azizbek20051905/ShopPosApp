from datetime import date

from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sales.models import Sale, SaleItem


class AnalyticsViewSet(viewsets.ViewSet):
  """
  Analytics endpoints.
  """

  @action(detail=False, methods=["get"], url_path="today")
  def today(self, request):
    """
    GET /api/analytics/today/
    Returns summary of today's sales and profit.
    """
    today = date.today()

    sales_qs = Sale.objects.filter(created_at__date=today)
    total_sales = sales_qs.aggregate(s=Sum("total_amount"))["s"] or 0
    total_profit = sales_qs.aggregate(s=Sum("total_profit"))["s"] or 0

    top_items = (
      SaleItem.objects.filter(sale__created_at__date=today)
      .values("product_id", "product__name")
      .annotate(quantity_sold=Sum("quantity"))
      .order_by("-quantity_sold")[:5]
    )

    top_products = [
      {
        "product_id": item["product_id"],
        "name": item["product__name"],
        "quantity_sold": float(item["quantity_sold"]),
      }
      for item in top_items
    ]

    return Response(
      {
        "total_sales": float(total_sales),
        "profit": float(total_profit),
        "top_products": top_products,
      }
    )

from django.shortcuts import render

# Create your views here.
