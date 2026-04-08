from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Tenant
from accounts.models import Profile
from subscriptions.models import Plan, Subscription

class TenantRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    store_name = serializers.CharField(max_length=255)
    subdomain = serializers.SlugField(max_length=64, required=False)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        tenant = Tenant.objects.create(
            name=validated_data['store_name'],
            owner=user,
            subdomain=validated_data.get('subdomain')
        )
        
        # Profile is created by signal, but we need to update it
        profile = user.profile
        profile.tenant = tenant
        profile.role = Profile.ADMIN
        profile.save()

        # Create a default 'Free Trial' plan if it doesn't exist
        trial_plan, _ = Plan.objects.get_or_create(
            name="7-Day Free Trial",
            defaults={
                "price": 0,
                "duration_days": 7,
                "description": "Full access for 7 days to test the platform."
            }
        )

        # Create the initial subscription
        Subscription.objects.create(
            tenant=tenant,
            plan=trial_plan,
            end_date=timezone.now() + timedelta(days=7),
            is_trial=True,
            status='active'
        )
        
        return tenant
