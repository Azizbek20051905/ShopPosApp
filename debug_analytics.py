import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastit_pos_backend.settings')
django.setup()

from sales.models import Sale
from django.db.models import Sum

def debug_analytics():
    today = timezone.localdate()
    print(f"Current System Date: {today}")
    
    total_sales = Sale.objects.count()
    print(f"Total Sales in DB: {total_sales}")
    
    # Check Today
    today_sales = Sale.objects.filter(created_at__date=today)
    print(f"Today's Sales Count: {today_sales.count()}")
    print(f"Today's Revenue: {today_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0}")
    
    # Check Week
    start_of_week = today - timedelta(days=today.weekday())
    week_sales = Sale.objects.filter(created_at__date__gte=start_of_week, created_at__date__lte=today)
    print(f"This Week's Sales Count: {week_sales.count()} (from {start_of_week} to {today})")
    print(f"This Week's Revenue: {week_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0}")
    
    # Check all sales by date
    from django.db.models.functions import TruncDate
    date_summary = Sale.objects.annotate(day=TruncDate('created_at')).values('day').annotate(count=Count('id'), rev=Sum('total_amount')).order_by('-day')
    print("\nSales Summary by Date:")
    for entry in date_summary:
        print(f"{entry['day']}: {entry['count']} orders, {entry['rev']} UZS")

if __name__ == "__main__":
    from django.db.models import Count
    debug_analytics()
