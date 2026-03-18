from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, F, Value, DecimalField
from django.db.models.functions import TruncDate, Coalesce
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from sales.models import Sale, SaleItem
from products.models import Product


def _get_date_range(period: str):
    """
    Returns (start_dt, end_dt) as timezone-aware datetimes.
    - today: start of today (00:00:00) to now
    - week: last 7 days including today
    - month: last 30 days including today
    - year: from Jan 1st of current year to now
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if period == 'today':
        return today_start, now
    elif period == 'week':
        return now - timedelta(days=7), now
    elif period == 'year':
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0), now
    else:  # month (default)
        return now - timedelta(days=30), now


class AnalyticsViewSet(viewsets.ViewSet):
    """
    Analytics endpoints.
    GET /api/analytics/?period=today|week|month|year
    """
    permission_classes = [IsAuthenticated]

    def list(self, request):
        period = request.query_params.get('period', 'month')
        start_dt, end_dt = _get_date_range(period)
        
        # Log for debugging
        print(f"DEBUG: Period={period}, Start={start_dt}, End={end_dt}")

        sales_qs = Sale.objects.filter(created_at__range=(start_dt, end_dt))

        # --- KPIs ---
        revenue = sales_qs.aggregate(s=Coalesce(Sum('total_amount'), Value(0, output_field=DecimalField())))['s']
        profit = sales_qs.aggregate(s=Coalesce(Sum('total_profit'), Value(0, output_field=DecimalField())))['s']
        orders = sales_qs.count()
        avg_order = float(revenue) / orders if orders > 0 else 0

        # --- Sales Trend (grouped by date) ---
        trend_qs = (
            sales_qs
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(revenue=Coalesce(Sum('total_amount'), Value(0, output_field=DecimalField())))
            .order_by('day')
        )
        trend = [
            {'date': item['day'].strftime('%Y-%m-%d'), 'revenue': float(item['revenue'])}
            for item in trend_qs
        ]

        # --- Category Distribution ---
        cat_qs = (
            SaleItem.objects
            .filter(sale__created_at__range=(start_dt, end_dt))
            .values(category=F('product__category__name'))
            .annotate(total=Coalesce(Sum('price_at_sale'), Value(0, output_field=DecimalField())))
            .order_by('-total')
        )
        total_rev = float(revenue) if float(revenue) > 0 else 1
        categories = []
        for item in cat_qs:
            cat_name = item['category'] or 'Uncategorized'
            pct = round(float(item['total']) / total_rev * 100, 1)
            categories.append({'category': cat_name, 'percent': pct})

        # --- Top Products ---
        top_items = (
            SaleItem.objects
            .filter(sale__created_at__range=(start_dt, end_dt))
            .values('product_id', 'product__name')
            .annotate(
                units=Coalesce(Sum('quantity'), Value(0, output_field=DecimalField())),
                revenue=Coalesce(Sum('price_at_sale'), Value(0, output_field=DecimalField())),
            )
            .order_by('-units')[:5]
        )
        top_products = [
            {
                'name': item['product__name'],
                'units': float(item['units']),
                'revenue': float(item['revenue']),
            }
            for item in top_items
        ]

        # --- Recent Sales (within selected period) ---
        recent_qs = sales_qs.order_by('-created_at')[:5]
        recent_sales = [
            {
                'id': s.id,
                'total': float(s.total_amount),
                'items': s.items.count(),
                'created_at': s.created_at.isoformat(),
            }
            for s in recent_qs
        ]

        return Response({
            'revenue': float(revenue),
            'profit': float(profit),
            'orders': orders,
            'avg_order': avg_order,
            'trend': trend,
            'categories': categories,
            'top_products': top_products,
            'recent_sales': recent_sales,
        })


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        today = timezone.localdate()
        yesterday = today - timedelta(days=1)

        # 1. Today's Sales
        today_sales = Sale.objects.filter(created_at__date=today).aggregate(
            s=Coalesce(Sum('total_amount'), Value(0, output_field=DecimalField())))['s']

        # 2. Yesterday's Sales
        yesterday_sales = Sale.objects.filter(created_at__date=yesterday).aggregate(
            s=Coalesce(Sum('total_amount'), Value(0, output_field=DecimalField())))['s']

        # 3. Today's Profit
        today_profit = Sale.objects.filter(created_at__date=today).aggregate(
            s=Coalesce(Sum('total_profit'), Value(0, output_field=DecimalField())))['s']

        # 4. Total Orders Today
        total_orders = Sale.objects.filter(created_at__date=today).count()

        # 5. Low Stock Products
        low_stock_qs = Product.objects.filter(stock_quantity__lte=F('min_stock'))[:5]
        low_stock_data = [
            {'id': p.id, 'name': p.name, 'stock': float(p.stock_quantity)}
            for p in low_stock_qs
        ]

        # 6. Recent Sales
        recent_sales_qs = Sale.objects.order_by('-created_at')[:5]
        recent_sales_data = [
            {
                'id': s.id,
                'total': float(s.total_amount),
                'items': s.items.count(),
                'created_at': s.created_at.isoformat(),
            }
            for s in recent_sales_qs
        ]

        return Response({
            'today_sales': float(today_sales),
            'yesterday_sales': float(yesterday_sales),
            'today_profit': float(today_profit),
            'total_orders': total_orders,
            'low_stock': low_stock_data,
            'recent_sales': recent_sales_data,
        })
