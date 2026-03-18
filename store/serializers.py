from rest_framework import serializers
from .models import StoreSettings, ActivityLog, PrinterSettings, HelpInfo


class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ['id', 'name', 'phone', 'address', 'city', 'district', 'currency', 'tax_percent']


class PrinterSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterSettings
        fields = ['id', 'printer_name', 'printer_ip', 'paper_size', 'auto_print']


class HelpInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpInfo
        fields = ['id', 'telegram', 'email']


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'detail', 'username', 'created_at']

    def get_username(self, obj):
        return obj.user.username if obj.user else 'System'
