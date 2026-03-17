from django.db import models
from django.contrib.auth.models import User


class StoreSettings(models.Model):
    name = models.CharField(max_length=200, default="My Store")
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
