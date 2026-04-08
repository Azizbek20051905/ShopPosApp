from rest_framework import viewsets

class TenantViewSetMixin:
    """
    Mixin to automatically filter querysets by the current user's tenant
    and assign the tenant when saving objects.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'profile') and self.request.user.profile.tenant:
            # Filter by tenant if the model has a tenant field
            if hasattr(queryset.model, 'tenant'):
                return queryset.filter(tenant=self.request.user.profile.tenant)
        return queryset.none()  # Return empty if no tenant associated

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'profile') and self.request.user.profile.tenant:
            serializer.save(tenant=self.request.user.profile.tenant)
        else:
            # This should ideally be caught by permissions, but as a fallback:
            raise Exception("User has no tenant assigned.")
