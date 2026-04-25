from django.shortcuts import render

def landing_view(request):
    return render(request, 'landing.html')

def auth_view(request):
    return render(request, 'auth.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def pos_view(request):
    return render(request, 'pos.html')

def manage_view(request):
    return render(request, 'management.html')

def billing_view(request):
    return render(request, 'billing.html')

def download_view(request):
    return render(request, 'download.html')
