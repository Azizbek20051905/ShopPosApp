from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    fields = ("product", "quantity", "price_at_sale", "profit")
    readonly_fields = ("product", "quantity", "price_at_sale", "profit")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "total_amount", "total_profit", "created_at")
    inlines = [SaleItemInline]
    date_hierarchy = "created_at"
    readonly_fields = ("total_amount", "total_profit")
