from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')
    phone = serializers.CharField(source='profile.phone', allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    # Permission fields
    can_use_pos = serializers.BooleanField(source='profile.can_use_pos', required=False)
    can_make_sale = serializers.BooleanField(source='profile.can_make_sale', required=False)
    can_view_products = serializers.BooleanField(source='profile.can_view_products', required=False)
    can_add_product = serializers.BooleanField(source='profile.can_add_product', required=False)
    can_edit_product = serializers.BooleanField(source='profile.can_edit_product', required=False)
    can_delete_product = serializers.BooleanField(source='profile.can_delete_product', required=False)
    can_view_inventory = serializers.BooleanField(source='profile.can_view_inventory', required=False)
    can_add_stock = serializers.BooleanField(source='profile.can_add_stock', required=False)
    can_view_analytics = serializers.BooleanField(source='profile.can_view_analytics', required=False)
    can_view_users = serializers.BooleanField(source='profile.can_view_users', required=False)
    can_add_user = serializers.BooleanField(source='profile.can_add_user', required=False)
    can_edit_user = serializers.BooleanField(source='profile.can_edit_user', required=False)
    can_delete_user = serializers.BooleanField(source='profile.can_delete_user', required=False)
    can_view_settings = serializers.BooleanField(source='profile.can_view_settings', required=False)
    can_edit_settings = serializers.BooleanField(source='profile.can_edit_settings', required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'email', 'first_name', 'last_name', 
            'role', 'phone', 'can_use_pos', 'can_make_sale', 'can_view_products', 
            'can_add_product', 'can_edit_product', 'can_delete_product', 
            'can_view_inventory', 'can_add_stock', 'can_view_analytics', 
            'can_view_users', 'can_add_user', 'can_edit_user', 'can_delete_user',
            'can_view_settings', 'can_edit_settings'
        ]

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        profile = user.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom user data into response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'role': self.user.profile.role if hasattr(self.user, 'profile') else 'cashier',
            'permissions': self.user.profile.permissions if hasattr(self.user, 'profile') else {},
        }
        return data
