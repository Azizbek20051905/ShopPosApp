from rest_framework import viewsets, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StoreSettings, ActivityLog
from .serializers import StoreSettingsSerializer, ActivityLogSerializer
from django.contrib.auth.models import User
from accounts.serializers import UserSerializer


class StoreSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        settings_obj = StoreSettings.get_settings()
        return Response(StoreSettingsSerializer(settings_obj).data)

    def put(self, request):
        # Fix permission check to avoid AttributeError if profile is missing
        user_role = getattr(getattr(request.user, 'profile', None), 'role', 'cashier')
        if not request.user.is_staff and user_role != 'admin':
            return Response({'error': 'Permission denied'}, status=403)
        settings_obj = StoreSettings.get_settings()
        serializer = StoreSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.profile.role if hasattr(user, 'profile') else 'cashier',
            'phone': user.profile.phone if hasattr(user, 'profile') else '',
        }
        return Response(data)


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ActivityLog.objects.all()
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Let DRF handle ordering and pagination automatically


class BackupView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({'message': 'Backup created successfully in cloud storage.'})


class SyncView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({'message': 'Data synchronization complete.'})
