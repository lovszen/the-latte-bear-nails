from django.shortcuts import render

def detalle_carrito(request):
    return render(request, 'carrito/detalle.html')