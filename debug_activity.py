import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastit_pos_backend.settings')
django.setup()

from store.models import ActivityLog
from store.serializers import ActivityLogSerializer

try:
    count = ActivityLog.objects.count()
    print(f"Total Logs: {count}")
    logs = ActivityLog.objects.all().order_by('-created_at')[:10]
    serializer = ActivityLogSerializer(logs, many=True)
    print("Serialization success!")
    # print(serializer.data)
except Exception as e:
    import traceback
    print(f"Error occurred: {e}")
    traceback.print_exc()
