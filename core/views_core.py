from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment_failure.html')

def payment_pending(request):
    return render(request, 'payment_pending.html')