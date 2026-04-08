from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ADMIN = 'admin'
    CASHIER = 'cashier'
    MANAGER = 'manager'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CASHIER, 'Cashier'),
        (MANAGER, 'Manager'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CASHIER)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # POS Permissions
    can_use_pos = models.BooleanField(default=True)
    can_make_sale = models.BooleanField(default=True)

    # Product Permissions
    can_view_products = models.BooleanField(default=True)
    can_add_product = models.BooleanField(default=False)
    can_edit_product = models.BooleanField(default=False)
    can_delete_product = models.BooleanField(default=False)

    # Inventory Permissions
    can_view_inventory = models.BooleanField(default=True)
    can_add_stock = models.BooleanField(default=False)

    # Analytics Permissions
    can_view_analytics = models.BooleanField(default=False)

    # User Permissions
    can_view_users = models.BooleanField(default=False)
    can_add_user = models.BooleanField(default=False)
    can_edit_user = models.BooleanField(default=False)
    can_delete_user = models.BooleanField(default=False)

    # Settings Permissions
    can_view_settings = models.BooleanField(default=False)
    can_edit_settings = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    @property
    def permissions(self):
        """Returns a dict of all permissions for this user."""
        if self.user.is_superuser:
            return {
                'can_use_pos': True, 'can_make_sale': True,
                'can_view_products': True, 'can_add_product': True, 
                'can_edit_product': True, 'can_delete_product': True,
                'can_view_inventory': True, 'can_add_stock': True,
                'can_view_analytics': True,
                'can_view_users': True, 'can_add_user': True, 
                'can_edit_user': True, 'can_delete_user': True,
                'can_view_settings': True, 'can_edit_settings': True,
            }
        
        return {
            'can_use_pos': self.can_use_pos,
            'can_make_sale': self.can_make_sale,
            'can_view_products': self.can_view_products,
            'can_add_product': self.can_add_product,
            'can_edit_product': self.can_edit_product,
            'can_delete_product': self.can_delete_product,
            'can_view_inventory': self.can_view_inventory,
            'can_add_stock': self.can_add_stock,
            'can_view_analytics': self.can_view_analytics,
            'can_view_users': self.can_view_users,
            'can_add_user': self.can_add_user,
            'can_edit_user': self.can_edit_user,
            'can_delete_user': self.can_delete_user,
            'can_view_settings': self.can_view_settings,
            'can_edit_settings': self.can_edit_settings,
        }

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
