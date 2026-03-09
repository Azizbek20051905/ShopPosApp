from django.contrib import admin
from .models import StockHistory


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ("product", "change_amount", "type", "created_at")
    list_filter = ("type",)
    search_fields = ("product__name", "product__barcode")
    date_hierarchy = "created_at"
