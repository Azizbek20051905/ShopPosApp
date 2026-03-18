from django.db import models
from django.contrib.auth.models import User


class StoreSettings(models.Model):
    name = models.CharField(max_length=200, default="My Store")
    phone = models.CharField(max_length=20, default="")
    address = models.CharField(max_length=500, default="")
    city = models.CharField(max_length=100, default="Tashkent")
    district = models.CharField(max_length=100, default="")
    currency = models.CharField(max_length=10, default="UZS")
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"

    def __str__(self):
        return self.name

    @classmethod
    def get_settings(cls):
        """Return the single settings object, creating it if it doesn't exist."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PrinterSettings(models.Model):
    PAPER_SIZES = [
        ('58mm', '58mm'),
        ('80mm', '80mm'),
    ]
    printer_name = models.CharField(max_length=200, default="Default Printer")
    printer_ip = models.GenericIPAddressField(null=True, blank=True)
    paper_size = models.CharField(max_length=10, choices=PAPER_SIZES, default='58mm')
    auto_print = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Printer Settings"
        verbose_name_plural = "Printer Settings"

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HelpInfo(models.Model):
    telegram = models.CharField(max_length=100, default="@support")
    email = models.EmailField(default="support@pos.com")

    class Meta:
        verbose_name = "Help Info"
        verbose_name_plural = "Help Info"

    @classmethod
    def get_info(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ActivityLog(models.Model):
    ACTIONS = [
        ('sale', 'Sale Created'),
        ('product_add', 'Product Added'),
        ('product_update', 'Product Updated'),
        ('stock_update', 'Stock Updated'),
        ('user_login', 'User Login'),
        ('user_create', 'User Created'),
        ('user_delete', 'User Deleted'),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='activities',
    )
    action = models.CharField(max_length=30, choices=ACTIONS)
    detail = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at:%Y-%m-%d %H:%M}"
