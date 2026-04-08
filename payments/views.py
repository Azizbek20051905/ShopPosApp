from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Payment
from subscriptions.models import Plan, Subscription

class InitializePaymentView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        POST /api/payments/initialize/
        {
            "plan_id": 1,
            "provider": "payme"
        }
        """
        plan_id = request.data.get('plan_id')
        provider = request.data.get('provider')
        
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response({"detail": "Plan not found."}, status=status.HTTP_404_NOT_FOUND)

        tenant = request.user.profile.tenant
        subscription = getattr(tenant, 'subscription', None)

        # Create a pending payment record
        payment = Payment.objects.create(
            tenant=tenant,
            subscription=subscription,
            amount=plan.price,
            provider=provider,
            status='pending'
        )

        # In a real app, you would generate a Payme/Click checkout URL here.
        # For this SaaS demo, we'll return a mock URL.
        mock_checkout_url = f"https://checkout.{provider}.uz/pay/{payment.id}"
        
        return Response({
            "payment_id": payment.id,
            "checkout_url": mock_checkout_url,
            "message": "Payment initialized. Redirect user to checkout_url."
        })

class MockPaymentSuccessView(generics.CreateAPIView):
    """
    Utility view to simulate a successful payment for testing.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        try:
            payment = Payment.objects.get(id=payment_id, tenant=request.user.profile.tenant)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=404)

        if payment.status == 'success':
            return Response({"detail": "Payment already processed."})

        # Process the success
        payment.status = 'success'
        payment.transaction_id = f"mock_tx_{payment.id}"
        payment.save()

        # Update or Create Subscription
        tenant = payment.tenant
        # We assume the plan info was stored or we fetch it from the amount/context
        # For simplicity, let's say we find the plan by price or it was passed
        plan = Plan.objects.filter(price=payment.amount).first()
        
        if not plan:
            return Response({"detail": "Plan could not be determined from payment."}, status=400)

        subscription, created = Subscription.objects.get_or_create(
            tenant=tenant,
            defaults={
                'plan': plan,
                'end_date': timezone.now() + timedelta(days=plan.duration_days),
                'status': 'active'
            }
        )

        if not created:
            # Extend existing subscription
            if subscription.end_date < timezone.now():
                subscription.end_date = timezone.now() + timedelta(days=plan.duration_days)
            else:
                subscription.end_date += timedelta(days=plan.duration_days)
            
            subscription.plan = plan
            subscription.status = 'active'
            subscription.save()

        return Response({
            "message": "Payment successful. Subscription updated.",
            "subscription_end": subscription.end_date
        })
