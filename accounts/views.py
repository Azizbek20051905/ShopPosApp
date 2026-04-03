from rest_framework import permissions, viewsets
from django.contrib.auth.models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import HasStaffPermission

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('profile').order_by('id')
    serializer_class = UserSerializer
    permission_classes = [HasStaffPermission]
    permission_map = {
        'list': 'can_view_users',
        'retrieve': 'can_view_users',
        'create': 'can_add_user',
        'update': 'can_edit_user',
        'partial_update': 'can_edit_user',
        'destroy': 'can_delete_user',
    }
