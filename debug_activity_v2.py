import os
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastit_pos_backend.settings')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from store.models import ActivityLog
from store.views import ActivityLogViewSet

try:
    factory = RequestFactory()
    request = factory.get('/api/activity/')
    user, _ = User.objects.get_or_create(username='testuser', is_staff=True)
    request.user = user
    
    # Create some logs
    ActivityLog.objects.create(user=user, action='sale', detail='Test sale')
    ActivityLog.objects.create(user=None, action='product_add', detail='Test system action')
    
    viewset = ActivityLogViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    
    print("Simulating list view...")
    response = viewset.list(request)
    print(f"Status Code: {response.status_code}")
    print(f"Data: {response.data}")
    
    # Clean up
    ActivityLog.objects.all().delete()
    
except Exception as e:
    import traceback
    print("Caught error during simulation:")
    traceback.print_exc()
