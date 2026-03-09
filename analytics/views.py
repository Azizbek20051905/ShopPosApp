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

  def list(self, request):
    """
    GET /api/analytics/
    Returns summary statistics for today and yesterday.
    """
    from datetime import timedelta
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Today's Sales & Profit
    today_qs = Sale.objects.filter(created_at__date=today)
    today_sales = today_qs.aggregate(s=Sum("total_amount"))["s"] or 0
    today_profit = today_qs.aggregate(p=Sum("total_profit"))["p"] or 0

    # Yesterday's Sales
    yesterday_qs = Sale.objects.filter(created_at__date=yesterday)
    yesterday_sales = yesterday_qs.aggregate(s=Sum("total_amount"))["s"] or 0

    # Top Product (Today)
    top_item = (
      SaleItem.objects.filter(sale__created_at__date=today)
      .values("product__name")
      .annotate(quantity_sold=Sum("quantity"))
      .order_by("-quantity_sold")
      .first()
    )
    top_product_name = top_item["product__name"] if top_item else "No sales yet"

    return Response(
      {
        "today_sales": float(today_sales),
        "yesterday_sales": float(yesterday_sales),
        "today_profit": float(today_profit),
        "top_product": top_product_name,
      }
    )

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
