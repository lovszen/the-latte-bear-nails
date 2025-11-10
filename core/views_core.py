from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html')

@login_required
def chat_view(request):
    return render(request, 'core/chat.html')

def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment_failure.html')

def payment_pending(request):
    return render(request, 'payment_pending.html')