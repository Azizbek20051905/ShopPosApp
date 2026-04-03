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


from django.db.models.functions import TruncDate, TruncMonth, ExtractHour, ExtractWeekDay

def _get_base_date(request):
    date_str = request.query_params.get('date')
    if date_str:
        try:
            return timezone.make_aware(timezone.datetime.strptime(date_str, '%Y-%m-%d'))
        except ValueError:
            pass
    return timezone.now()

from accounts.permissions import HasStaffPermission


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [HasStaffPermission]
    permission_map = {'list': 'can_view_analytics'}

    def list(self, request):
        period = request.query_params.get('period', 'month')
        base_date = _get_base_date(request)
        
        # --- Date Range Calculation ---
        if period == 'today':
            start_dt = base_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(days=1)
        elif period == 'week':
            # Start of the week (Monday)
            start_dt = (base_date - timedelta(days=base_date.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(days=7)
        elif period == 'year':
            start_dt = base_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_dt = start_dt.replace(year=start_dt.year + 1)
        else:  # month
            start_dt = base_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Next month start
            if start_dt.month == 12:
                end_dt = start_dt.replace(year=start_dt.year + 1, month=1)
            else:
                end_dt = start_dt.replace(month=start_dt.month + 1)

        sales_qs = Sale.objects.filter(created_at__range=(start_dt, end_dt))

        # --- KPIs ---
        revenue = sales_qs.aggregate(s=Coalesce(Sum('total_amount'), Value(0, output_field=DecimalField())))['s']
        profit = sales_qs.aggregate(s=Coalesce(Sum('total_profit'), Value(0, output_field=DecimalField())))['s']
        orders = sales_qs.count()
        avg_order = float(revenue) / orders if orders > 0 else 0

        # --- Trend Logic with Padding ---
        trend = []
        if period == 'today':
            # Group by Hour (0-23)
            trend_data = (
                sales_qs.annotate(h=ExtractHour('created_at'))
                .values('h')
                .annotate(revenue=Sum('total_amount'))
                .values('h', 'revenue')
            )
            lookup = {item['h']: float(item['revenue']) for item in trend_data}
            for h in range(24):
                trend.append({'label': f"{h:02d}:00", 'revenue': lookup.get(h, 0.0)})

        elif period == 'week':
            # Group by Day (Mon-Sun)
            trend_data = (
                sales_qs.annotate(d=TruncDate('created_at'))
                .values('d')
                .annotate(revenue=Sum('total_amount'))
            )
            lookup = {item['d'].strftime('%Y-%m-%d'): float(item['revenue']) for item in trend_data}
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            for i in range(7):
                curr_date = start_dt + timedelta(days=i)
                date_key = curr_date.strftime('%Y-%m-%d')
                trend.append({'label': days[i], 'date': date_key, 'revenue': lookup.get(date_key, 0.0)})

        elif period == 'year':
            # Group by Month (Jan-Dec)
            trend_data = (
                sales_qs.annotate(m=TruncMonth('created_at'))
                .values('m')
                .annotate(revenue=Sum('total_amount'))
            )
            lookup = {item['m'].month: float(item['revenue']) for item in trend_data}
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for m in range(1, 13):
                trend.append({'label': months[m-1], 'revenue': lookup.get(m, 0.0)})

        else:  # month
            # Group by Days of Month (1-31)
            trend_data = (
                sales_qs.annotate(d=TruncDate('created_at'))
                .values('d')
                .annotate(revenue=Sum('total_amount'))
            )
            lookup = {item['d'].day: float(item['revenue']) for item in trend_data}
            last_day = (end_dt - timedelta(days=1)).day
            for d in range(1, last_day + 1):
                trend.append({'label': str(d), 'revenue': lookup.get(d, 0.0)})

        # Category Distribution
        cat_qs = (
            SaleItem.objects
            .filter(sale__created_at__range=(start_dt, end_dt))
            .values(category=F('product__category__name'))
            .annotate(total=Sum('profit')) # Using profit for distribution or total? usually revenue
            .annotate(rev=Sum('price_at_sale'))
            .order_by('-rev')
        )
        total_rev = float(revenue) or 1
        categories = []
        for item in cat_qs:
            cat_name = item['category'] or 'Uncategorized'
            pct = round(float(item['rev']) / total_rev * 100, 1)
            categories.append({'category': cat_name, 'percent': pct})

        # Top Products
        top_items = (
            SaleItem.objects
            .filter(sale__created_at__range=(start_dt, end_dt))
            .values('product__name')
            .annotate(
                units=Sum('quantity'),
                revenue=Sum('price_at_sale'),
            )
            .order_by('-units')[:5]
        )
        top_products = [
            {'name': item['product__name'], 'units': float(item['units']), 'revenue': float(item['revenue'])}
            for item in top_items
        ]

        # Recent Sales
        recent_qs = sales_qs.order_by('-created_at')[:5]
        recent_sales = [
            {'id': s.id, 'total': float(s.total_amount), 'items': s.items.count(), 'created_at': s.created_at.isoformat()}
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
    permission_classes = [HasStaffPermission]
    permission_map = {'list': 'can_view_analytics'}

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
