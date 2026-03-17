from django.contrib import admin
from .models import StoreSettings, ActivityLog

@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'district', 'currency', 'tax_percent']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'detail', 'created_at']
    list_filter = ['action']
    readonly_fields = ['created_at']
