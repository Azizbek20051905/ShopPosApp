from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role')
    phone = serializers.CharField(source='profile.phone', allow_blank=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'role', 'phone']

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        # Profile is created by signal, just update it
        profile = user.profile
        profile.role = profile_data.get('role', profile.role)
        profile.phone = profile_data.get('phone', profile.phone)
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
        profile.role = profile_data.get('role', profile.role)
        profile.phone = profile_data.get('phone', profile.phone)
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
        }
        return data
