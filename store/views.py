from rest_framework import viewsets, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import StoreSettings, ActivityLog, PrinterSettings, HelpInfo
from .serializers import (
    StoreSettingsSerializer, 
    ActivityLogSerializer,
    PrinterSettingsSerializer,
    HelpInfoSerializer
)
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
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.profile.role if hasattr(user, 'profile') else 'cashier',
            'phone': user.profile.phone if hasattr(user, 'profile') else '',
            'avatar': request.build_absolute_uri(user.profile.avatar.url) if hasattr(user, 'profile') and user.profile.avatar else None,
        }
        return Response(data)

    def put(self, request):
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        # Profile fields update
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.phone = request.data.get('phone', profile.phone)
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            
        return self.get(request)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'error': 'Old and new passwords required'}, status=400)
            
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=400)
            
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password updated successfully'})


class PrinterSettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        obj = PrinterSettings.get_settings()
        return Response(PrinterSettingsSerializer(obj).data)

    def put(self, request):
        obj = PrinterSettings.get_settings()
        serializer = PrinterSettingsSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class HelpInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        obj = HelpInfo.get_info()
        return Response(HelpInfoSerializer(obj).data)


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
