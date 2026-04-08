from django.db import models
from django.utils import timezone
from datetime import timedelta

class Plan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    description = models.TextField(blank=True)
    
    # Feature limits (optional)
    max_products = models.IntegerField(default=-1) # -1 for unlimited
    max_staff = models.IntegerField(default=-1)
    
    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} - {self.price} UZS"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('canceled', 'Canceled'),
    ]
    
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_trial = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name} ({self.status})"

    def is_currently_active(self):
        return self.status == 'active' and self.end_date > timezone.now()

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)
