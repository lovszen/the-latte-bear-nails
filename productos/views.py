from django.shortcuts import render

# Create your views here.

from .models import Producto

def lista_productos(request): 
    productos = Producto.objects.all()
    return render(request, 'productos/tienda.html', {'productos': productos})