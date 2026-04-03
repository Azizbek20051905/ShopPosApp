from rest_framework import permissions

class HasStaffPermission(permissions.BasePermission):
    """
    Custom permission to check if a user has a specific staff permission.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Superusers can do anything
        if request.user.is_superuser:
            return True
            
        # Get permission map from view
        # Example: permission_map = {'list': 'can_view_products', 'create': 'can_add_product'}
        permission_map = getattr(view, 'permission_map', {})
        required_perm = permission_map.get(view.action)
        
        if not required_perm:
            return True # If no specific permission mapped, allow (assuming authenticated)
            
        if hasattr(request.user, 'profile'):
            return getattr(request.user.profile, required_perm, False)
            
        return False
