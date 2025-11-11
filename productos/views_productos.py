from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Producto
from django.http import JsonResponse
import json

def is_staff_user(user):
    return user.is_staff

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/tienda.html', {'productos': productos})

@login_required
@user_passes_test(is_staff_user)
def admin_agregar_producto(request):
    from productos.models import Producto
    from productos.forms import ProductoForm
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Producto agregado exitosamente!')
            return redirect('admin_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'admin/agregar_producto.html', {'form': form})

@login_required
def personalizado(request):
    if request.method == 'POST':
        forma = request.POST.get('forma')
        largo_str = request.POST.get('largo')
        medidas = request.POST.get('medidas')

        try:
            largo = int(largo_str)
        except (TypeError, ValueError):
            messages.error(request, 'El largo de la uña debe ser un número válido.')
            return render(request, 'productos/personalizado.html', {})

        if forma and largo and medidas:
            from core.models import PersonalizedRequest
            PersonalizedRequest.objects.create(
                user=request.user,
                forma=forma,
                largo=largo,
                medidas=medidas,
                status='pending'
            )
            
            messages.success(request, '¡Tu solicitud de personalización ha sido enviada con éxito! La revisaremos y la verás en Presupuestos pronto.')
            return redirect('budgets_list')
        else:
            messages.error(request, 'Por favor, completa todos los campos del formulario.')
    
    return render(request, 'productos/personalizado.html')

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