from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sales.models import Sale, SaleItem
from products.models import Product


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

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        # 1. Today's Sales
        today_sales = Sale.objects.filter(created_at__date=today).aggregate(s=Sum("total_amount"))["s"] or 0

        # 2. Yesterday's Sales
        yesterday_sales = Sale.objects.filter(created_at__date=yesterday).aggregate(s=Sum("total_amount"))["s"] or 0

        # 3. Today's Profit
        today_profit = Sale.objects.filter(created_at__date=today).aggregate(s=Sum("total_profit"))["s"] or 0

        # 4. Total Orders Today
        total_orders = Sale.objects.filter(created_at__date=today).count()

        # 5. Low Stock Products
        # Using the newly added min_stock field
        low_stock_qs = Product.objects.filter(stock_quantity__lte=F("min_stock"))[:5]
        low_stock_data = [
            {"id": p.id, "name": p.name, "stock": float(p.stock_quantity)}
            for p in low_stock_qs
        ]

        # 6. Recent Sales
        recent_sales_qs = Sale.objects.order_by("-created_at")[:5]
        recent_sales_data = [
            {
                "id": s.id,
                "total": float(s.total_amount),
                "items": s.items.count(),
                "created_at": s.created_at.isoformat()
            }
            for s in recent_sales_qs
        ]

        return Response({
            "today_sales": float(today_sales),
            "yesterday_sales": float(yesterday_sales),
            "today_profit": float(today_profit),
            "total_orders": total_orders,
            "low_stock": low_stock_data,
            "recent_sales": recent_sales_data
        })
