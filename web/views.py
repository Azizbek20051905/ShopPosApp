from django.shortcuts import render
from django.contrib.auth.decorators import login_with_redirect_url # actually use regular render

def landing_view(request):
    return render(request, 'landing.html')

def auth_view(request):
    return render(request, 'auth.html')

def pos_view(request):
    # The actual authentication is handled by JS in the template
    return render(request, 'pos.html')

def billing_view(request):
    return render(request, 'billing.html') # Need to create this
