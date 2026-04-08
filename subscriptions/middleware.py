from django.http import JsonResponse
from django.urls import resolve
from django.utils import timezone
from .models import Subscription

class SubscriptionMiddleware:
    """
    Middleware to check if the tenant's subscription is active.
    Blocks access to POS and management APIs if expired.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude specific paths like admin, login, registration, and billing
        path = request.path
        if any(path.startswith(x) for x in [
            '/admin/', 
            '/api/tenants/register/', 
            '/api/accounts/login/', # Adjust if using JWT
            '/api/token/',           # JWT tokens
            '/api/subscriptions/plans/', # Allow viewing plans
            '/api/payments/',        # Allow payments
        ]):
            return self.get_response(request)

        # Check if user is authenticated and has a tenant
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile') and request.user.profile.tenant:
                tenant = request.user.profile.tenant
                
                # Check for active subscription
                subscription = Subscription.objects.filter(tenant=tenant).first()
                
                if not subscription or not subscription.is_currently_active():
                    # If it's a GET request to some basic info, maybe allow? 
                    # For now, block everything except the explicit allows above.
                    return JsonResponse({
                        "detail": "Subscription expired or inactive. Please renew your plan to continue.",
                        "code": "subscription_required",
                        "billing_url": "/billing/" # Frontend URL
                    }, status=402) # 402 Payment Required

        return self.get_response(request)
