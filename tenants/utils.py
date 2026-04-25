from rest_framework import viewsets

class TenantViewSetMixin:
    """
    Mixin to automatically filter querysets by the current user's tenant
    and assign the tenant when saving objects.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Superusers can see everything
        if self.request.user.is_superuser:
            return queryset
            
        if hasattr(self.request.user, 'profile') and self.request.user.profile.tenant:
            # Filter by tenant if the model has a tenant field
            if hasattr(queryset.model, 'tenant'):
                return queryset.filter(tenant=self.request.user.profile.tenant)
        
        # Fallback: if user has no tenant, show objects with no tenant
        if hasattr(queryset.model, 'tenant'):
            return queryset.filter(tenant__isnull=True)
            
        return queryset

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'profile') and self.request.user.profile.tenant:
            serializer.save(tenant=self.request.user.profile.tenant)
        else:
            # For superusers or users without a profile/tenant, save without tenant
            serializer.save()
