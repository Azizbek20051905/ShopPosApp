from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import TenantRegistrationSerializer

class TenantRegistrationView(generics.CreateAPIView):
    serializer_class = TenantRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        
        return Response({
            "message": "Tenant and User created successfully.",
            "tenant": {
                "id": tenant.id,
                "name": tenant.name,
                "subdomain": tenant.subdomain,
            },
            "user": {
                "username": tenant.owner.username,
                "email": tenant.owner.email,
            }
        }, status=status.HTTP_201_CREATED)
