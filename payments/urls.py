from django.urls import path
from .views import InitializePaymentView, MockPaymentSuccessView

urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='payment-initialize'),
    path('mock-success/', MockPaymentSuccessView.as_view(), name='payment-mock-success'),
]
