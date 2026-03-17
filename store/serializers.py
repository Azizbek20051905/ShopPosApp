from rest_framework import serializers
from .models import StoreSettings, ActivityLog


class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['id', 'name', 'city', 'district', 'currency', 'tax_percent']


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'detail', 'username', 'created_at']

    def get_username(self, obj):
        return obj.user.username if obj.user else 'System'
