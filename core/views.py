from django.shortcuts import render

def home(request):
    return render(request, 'home.html')

def lista_productos(request):
    return render(request, 'lista_productos.html')