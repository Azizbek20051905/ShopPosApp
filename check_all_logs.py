import os
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastit_pos_backend.settings')

import django
django.setup()

from store.models import ActivityLog
from store.serializers import ActivityLogSerializer

print(f"Total Logs in DB: {ActivityLog.objects.count()}")

error_count = 0
for log in ActivityLog.objects.all():
    try:
        data = ActivityLogSerializer(log).data
    except Exception as e:
        print(f"Error serializing log ID {log.id}: {e}")
        error_count += 1

if error_count == 0:
    print("All logs serialized successfully!")
else:
    print(f"Found {error_count} problematic logs.")
