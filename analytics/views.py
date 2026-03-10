from datetime import date, timedelta
from django.db.models import Sum
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from sales.models import Sale, SaleItem

class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints for POS dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """
        GET /api/analytics/
        Returns comprehensive sales and product analytics.
        """
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Sales aggregations
        today_sales = Sale.objects.filter(created_at__date=today).aggregate(
            s=Sum("total_amount")
        )["s"] or 0
        
        yesterday_sales = Sale.objects.filter(created_at__date=yesterday).aggregate(
            s=Sum("total_amount")
        )["s"] or 0
        
        total_sales = Sale.objects.aggregate(
            s=Sum("total_amount")
        )["s"] or 0

        # Top 5 products by total quantity sold
        top_items = (
            SaleItem.objects.values("product__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        top_products = [
            {
                "product": item["product__name"],
                "total_quantity": float(item["total_quantity"]),
            }
            for item in top_items
        ]

        return Response({
            "today_sales": float(today_sales),
            "yesterday_sales": float(yesterday_sales),
            "total_sales": float(total_sales),
            "top_products": top_products,
        })
