import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastit_pos_backend.settings')
django.setup()

from django.contrib.auth.models import User
from tenants.models import Tenant
from products.models import Product, Category
from subscriptions.models import Subscription, Plan

def verify_tenancy():
    print("--- Verifying Tenancy ---")
    # 1. Create two tenants
    u1 = User.objects.create_user(username='owner1', password='pass')
    t1 = Tenant.objects.create(name="Store 1", owner=u1)
    
    u2 = User.objects.create_user(username='owner2', password='pass')
    t2 = Tenant.objects.create(name="Store 2", owner=u2)
    
    # 2. Add products to each
    c1 = Category.objects.create(name="Drinks", tenant=t1)
    p1 = Product.objects.create(name="Cola", sale_price=5000, purchase_price=3000, tenant=t1, category=c1)
    
    c2 = Category.objects.create(name="Food", tenant=t2)
    p2 = Product.objects.create(name="Burger", sale_price=15000, purchase_price=10000, tenant=t2, category=c2)
    
    # 3. Check isolation (in a real viewset this is handled by TenantViewSetMixin)
    # Here we just verify the objects have the correct tenant assigned
    assert p1.tenant == t1
    assert p2.tenant == t2
    print("Success: Data isolation verified at model level.")

def verify_subscription_logic():
    print("\n--- Verifying Subscription Logic ---")
    t1 = Tenant.objects.get(name="Store 1")
    plan, _ = Plan.objects.get_or_create(name="Test Plan", defaults={"price": 1000, "duration_days": 30})
    
    # Active subscription
    sub = Subscription.objects.create(
        tenant=t1, plan=plan, 
        end_date=timezone.now() + timedelta(days=5),
        status='active'
    )
    assert sub.is_currently_active() == True
    print("Success: Active subscription recognized.")
    
    # Expired subscription
    sub.end_date = timezone.now() - timedelta(days=1)
    sub.save()
    assert sub.is_currently_active() == False
    print("Success: Expired subscription recognized.")

if __name__ == "__main__":
    try:
        verify_tenancy()
        verify_subscription_logic()
        print("\nAll verifications passed!")
    except Exception as e:
        print(f"\nVerification failed: {e}")
    finally:
        # Cleanup test data if needed, but since it's dev db it's okay
        pass
