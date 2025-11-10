from django.shortcuts import render
from .models import Producto
from django.http import JsonResponse
import json

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/tienda.html', {'productos': productos})


def detalle_producto_api(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        producto_data = {
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'descripcion': producto.descripcion,
            'forma': producto.forma,
            'forma_display': producto.get_forma_display() if hasattr(producto, 'get_forma_display') else producto.forma,
            'tamaño': producto.tamaño,
            'tamaño_display': producto.get_tamaño_display() if hasattr(producto, 'get_tamaño_display') else producto.tamaño,
            'color_principal': producto.color_principal,
            'color_principal_display': producto.get_color_principal_display() if hasattr(producto, 'get_color_principal_display') else producto.color_principal,
            'color_secundario': producto.color_secundario,
            'color_secundario_display': producto.get_color_secundario_display() if hasattr(producto, 'get_color_secundario_display') else producto.color_secundario,
            'imagen': producto.imagen.url if producto.imagen else None,
        }
        
        return JsonResponse(producto_data)
        
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)