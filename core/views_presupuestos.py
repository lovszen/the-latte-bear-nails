# core/views_presupuestos.py - ARCHIVO COMPLETO CORREGIDO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core import serializers
from .models import Budget, BudgetItem, PersonalizedRequest
from .utils import generate_budget_pdf, send_budget_email
from productos.models import Producto
from django.http import HttpResponse
import threading
import logging
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Sum, Count

def is_staff_user(user):
    return user.is_staff


@staff_member_required
def admin_view_budget(request, budget_id):
    presupuesto = get_object_or_404(Budget, id=budget_id)
    return render(request, 'core/view_budget.html', {'presupuesto': presupuesto})

@login_required
@user_passes_test(is_staff_user)
def admin_gestion_presupuestos(request):
    """Vista de administración para gestionar presupuestos"""
    # Obtener todos los presupuestos
    presupuestos = Budget.objects.select_related('user').order_by('-created_at')
    
    # Estadísticas
    total_presupuestos = presupuestos.count()
    
    # Presupuestos de los últimos 30 días
    fecha_30_dias = timezone.now() - timedelta(days=30)
    presupuestos_30_dias = Budget.objects.filter(
        created_at__gte=fecha_30_dias
    ).count()
    
    # Presupuestos antiguos (más de 30 días)
    presupuestos_antiguos = Budget.objects.filter(
        created_at__lt=fecha_30_dias
    ).count()
    
    # Total de ingresos (suma de todos los presupuestos)
    total_ingresos = Budget.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    context = {
        'presupuestos': presupuestos,
        'total_presupuestos': total_presupuestos,
        'presupuestos_30_dias': presupuestos_30_dias,
        'presupuestos_antiguos': presupuestos_antiguos,
        'total_ingresos': total_ingresos,
    }
    
    return render(request, 'admin/admin_presupuestos.html', context) 

@login_required
@user_passes_test(is_staff_user)
def eliminar_presupuestos_masivos(request):
    """Eliminar presupuestos seleccionados masivamente"""
    if request.method == 'POST':
        presupuesto_ids = request.POST.get('presupuesto_ids', '')
        
        if presupuesto_ids:
            # Si vienen IDs específicos
            ids_list = [int(id) for id in presupuesto_ids.split(',') if id.isdigit()]
            presupuestos = Budget.objects.filter(id__in=ids_list)
            cantidad = presupuestos.count()
            presupuestos.delete()
            
            messages.success(request, f'Se eliminaron {cantidad} presupuestos')
        else:
            # Eliminar automáticamente los antiguos (más de 30 días)
            fecha_limite = timezone.now() - timedelta(days=30)
            presupuestos_antiguos = Budget.objects.filter(
                created_at__lt=fecha_limite
            )
            cantidad = presupuestos_antiguos.count()
            presupuestos_antiguos.delete()
            
            messages.success(request, f'Se eliminaron {cantidad} presupuestos antiguos')
    
    return redirect('admin_gestion_presupuestos')

@login_required
@user_passes_test(is_staff_user)
def limpiar_presupuestos_prueba(request):
    """Limpiar presupuestos de prueba"""
    if request.method == 'POST':
        # Filtros para identificar presupuestos de prueba
        presupuestos_prueba = Budget.objects.filter(
            Q(user__email__icontains='test') |
            Q(user__username__icontains='test') |
            Q(user__email__icontains='example') |
            Q(user__username__icontains='demo') |
            Q(total_amount=0) |
            Q(title__icontains='prueba') |
            Q(title__icontains='test') |
            Q(title__icontains='ejemplo') |
            Q(customer_name__icontains='test') |
            Q(customer_name__icontains='demo')
        )
        
        cantidad = presupuestos_prueba.count()
        presupuestos_prueba.delete()
        
        messages.success(request, f'Se eliminaron {cantidad} presupuestos de prueba')
    
    return redirect('admin_gestion_presupuestos')

# =============================================
# VIEWS EXISTENTES (TUS FUNCIONES ORIGINALES) - CORREGIDAS
# =============================================

@login_required
@user_passes_test(is_staff_user)
def admin_todos_presupuestos(request):
    budgets = Budget.objects.all().order_by('-created_at')
    return render(request, 'admin/todos_presupuestos.html', {
        'budgets': budgets
    })

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    from productos.models import Producto
    
    total_productos = Producto.objects.count()
    solicitudes_pendientes = PersonalizedRequest.objects.filter(status='pending').count()
    presupuestos_totales = Budget.objects.count()
    
    return render(request, 'admin/dashboard.html', {
        'total_productos': total_productos,
        'solicitudes_pendientes': solicitudes_pendientes,
        'presupuestos_totales': presupuestos_totales,
    })

@login_required
@user_passes_test(is_staff_user)
def admin_agregar_producto(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio = request.POST.get('precio')
            forma = request.POST.get('forma')
            tamaño = request.POST.get('tamaño')
            color_principal = request.POST.get('color_principal')
            color_secundario = request.POST.get('color_secundario')
            imagen = request.FILES.get('imagen')
            
            if not nombre or not precio or not color_principal:
                messages.error(request, '❌ Nombre, precio y color principal son obligatorios.')
                return render(request, 'admin/agregar_producto.html')
            
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion or '',
                precio=float(precio),
                forma=forma or 'almendra',
                tamaño=tamaño or 's',
                color_principal=color_principal,
                color_secundario=color_secundario or None,
            )
            
            if imagen:
                producto.imagen = imagen
            
            producto.save()
            
            messages.success(request, '✅ Producto agregado exitosamente!')
            return redirect('admin_productos')
            
        except Exception as e:
            messages.error(request, f'❌ Error al agregar el producto: {str(e)}')
            return render(request, 'admin/agregar_producto.html')
    
    return render(request, 'admin/agregar_producto.html')

@login_required
@user_passes_test(is_staff_user)
def admin_editar_producto(request, producto_id):
    from productos.models import Producto
    from productos.forms import ProductoForm
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Producto actualizado exitosamente!')
            return redirect('admin_productos')
    else:
        form = ProductoForm(instance=producto)
    
    return render(request, 'admin/editar_producto.html', {'form': form, 'producto': producto})

@login_required
@user_passes_test(is_staff_user)
def admin_eliminar_producto(request, producto_id):
    from productos.models import Producto
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        producto.delete()
        messages.success(request, '✅ Producto eliminado exitosamente!')
    
    return redirect('admin_productos')

@login_required
@user_passes_test(is_staff_user)
def admin_productos_lista(request):
    from productos.models import Producto
    productos = Producto.objects.all().order_by('-id')
    return render(request, 'admin/productos_lista.html', {'productos': productos})

@login_required
@user_passes_test(is_staff_user)
def admin_solicitudes_pendientes(request):
    solicitudes_pendientes = PersonalizedRequest.objects.filter(
        status='pending'
    ).select_related('user').order_by('-created_at')
    
    solicitudes_cotizadas = PersonalizedRequest.objects.filter(
        status='quoted'
    ).select_related('user').order_by('-created_at')
    
    return render(request, 'admin/solicitudes_admin.html', {
        'solicitudes_pendientes': solicitudes_pendientes,
        'solicitudes_cotizadas': solicitudes_cotizadas
    })

@login_required
@user_passes_test(is_staff_user)
def convert_request_to_budget(request, request_id):
    personalized_request = get_object_or_404(PersonalizedRequest, id=request_id)
    
    if personalized_request.related_budget:
        messages.warning(request, f'La solicitud #{request_id} ya fue presupuestada.')
        return redirect('view_budget', budget_id=personalized_request.related_budget.id)

    products = Producto.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        customer_name = personalized_request.user.username
        customer_email = personalized_request.user.email
        
        imagen_referencia = request.FILES.get('imagen_referencia')
        
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        precios = request.POST.getlist('precios')
        
        if not product_ids or not quantities:
            messages.error(request, 'Debes agregar al menos un producto con su cantidad.')
            products_json = serializers.serialize("json", products, fields=('nombre', 'precio'))
            return render(request, 'admin/convert_request.html', {
                'request': personalized_request,
                'products': products_json
            })

        budget = Budget.objects.create(
            user=personalized_request.user,
            title=title,
            customer_name=customer_name,
            customer_email=customer_email,
            total_amount=0,
            imagen_referencia=imagen_referencia
        )
        
        try:
            total = 0
            for product_id, quantity_str, precio_str in zip(product_ids, quantities, precios):
                product = Producto.objects.get(id=product_id)
                quantity = int(quantity_str)
                precio = float(precio_str)
                
                if quantity > 0:
                    item_total = precio * quantity
                    total += item_total
                    
                    BudgetItem.objects.create(
                        budget=budget,
                        product=product,
                        quantity=quantity,
                        price=precio
                    )
            
            budget.total_amount = total
            budget.save()
            
            personalized_request.status = 'quoted'
            personalized_request.related_budget = budget
            personalized_request.save()
            
            pdf_buffer = generate_budget_pdf(budget)
            _send_email_async(budget, pdf_buffer)

            messages.success(request, f'Presupuesto #{budget.id} creado con éxito!')
            return redirect('view_budget', budget_id=budget.id)

        except Exception as e:
            budget.delete()
            messages.error(request, f'Error al crear el presupuesto: {e}')
            return redirect('budgets_list')
    
    products_json = serializers.serialize("json", products, fields=('nombre', 'precio'))
    return render(request, 'admin/convert_request.html', {
        'request': personalized_request,
        'products': products_json
    })

@login_required
def create_personalized_request(request):
    if request.method == 'POST':
        forma = request.POST.get('forma')
        largo_str = request.POST.get('largo')
        medidas = request.POST.get('medidas')

        try:
            largo = int(largo_str)
        except (TypeError, ValueError):
            messages.error(request, 'El largo de la uña debe ser un número válido.')
            return render(request, 'personalizado.html', {})

        if forma and largo and medidas:
            PersonalizedRequest.objects.create(
                user=request.user,
                forma=forma,
                largo=largo,
                medidas=medidas,
            )
            
            messages.success(request, '¡Tu solicitud de personalización ha sido enviada con éxito! La revisaremos y la verás en Presupuestos pronto.')
            return redirect('budgets_list')
        else:
            messages.error(request, 'Por favor, completa todos los campos del formulario.')
            
    return render(request, 'personalizado.html', {})

@login_required
def download_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    pdf_buffer = generate_budget_pdf(budget)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="presupuesto_{budget.id}.pdf"'
    return response

@login_required
def budgets_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    personalized_requests = PersonalizedRequest.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'budgets/budgets_list.html', {
        'budgets': budgets,
        'personalized_requests': personalized_requests
    })

# VIEW CORREGIDA - PERMITE A ADMINS VER CUALQUIER PRESUPUESTO
@login_required
def view_budget(request, budget_id):
    """Vista para ver presupuestos - Admins pueden ver cualquier presupuesto"""
    if request.user.is_staff:
        # Admin puede ver cualquier presupuesto
        budget = get_object_or_404(Budget, id=budget_id)
    else:
        # Usuario normal solo puede ver sus propios presupuestos
        budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    return render(request, 'budgets/view_budget.html', {'budget': budget})

# NUEVA VIEW PARA QUE ADMINS PUEDAN ELIMINAR CUALQUIER PRESUPUESTO
@login_required
@user_passes_test(is_staff_user)
def admin_delete_budget(request, budget_id):
    """Los admins pueden eliminar cualquier presupuesto"""
    budget = get_object_or_404(Budget, id=budget_id)
    
    if request.method == 'POST':
        budget_title = budget.title
        budget.delete()
        messages.success(request, f'✅ Presupuesto "{budget_title}" eliminado exitosamente!')
        return redirect('admin_gestion_presupuestos')
    
    return redirect('admin_gestion_presupuestos')

@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.title = request.POST.get('title')
        budget.customer_name = request.POST.get('customer_name')
        budget.customer_email = request.POST.get('customer_email')
        
        budget.items.all().delete()
        
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        
        total = 0
        for product_id, quantity in zip(product_ids, quantities):
            product = Producto.objects.get(id=product_id)
            item_total = float(product.precio) * int(quantity)
            total += item_total
            
            BudgetItem.objects.create(
                budget=budget,
                product=product,
                quantity=quantity,
                price=product.precio
            )
        
        budget.total_amount = total
        budget.save()
        
        return redirect('view_budget', budget_id=budget.id)
    
    products = Producto.objects.all()
    return render(request, 'budgets/edit_budget.html', {
        'budget': budget,
        'products': products
    })

@login_required
def delete_budget(request, budget_id):
    """Usuarios normales solo pueden eliminar sus propios presupuestos"""
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    return redirect('budgets_list')

@login_required
def create_budget(request):
    if request.method == 'POST':
        return _handle_budget_creation(request)
    
    products = Producto.objects.all()
    return render(request, 'budgets/create_budget.html', {'products': products})

@login_required
def create_budget_from_cart(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    return _handle_budget_creation(request, is_ajax=True)

@login_required
def generate_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    return JsonResponse({'success': True, 'message': 'Presupuesto generado'})

def _handle_budget_creation(request, is_ajax=False):
    try:
        title = request.POST.get('title')
        customer_name = request.POST.get('customer_name') or request.user.username
        customer_email = request.POST.get('customer_email') or request.user.email
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Falta título'}) if is_ajax else redirect('create_budget')
        
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        
        if len(product_ids) != len(quantities):
            error = 'Productos y cantidades no coinciden'
            return JsonResponse({'success': False, 'error': error}) if is_ajax else redirect('create_budget')
        
        budget = Budget.objects.create(
            user=request.user,
            title=title,
            customer_name=customer_name,
            customer_email=customer_email,
            total_amount=0
        )
        
        total = _add_budget_items(budget, product_ids, quantities)
        budget.total_amount = total
        budget.save()
        
        pdf_buffer = generate_budget_pdf(budget)
        _send_email_async(budget, pdf_buffer)
        
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Presupuesto creado exitosamente'})
        return redirect('view_budget', budget_id=budget.id)
            
    except Exception as e:
        if is_ajax:
            return JsonResponse({'success': False, 'error': str(e)})
        return redirect('create_budget')

def _add_budget_items(budget, product_ids, quantities):
    total = 0
    for product_id, quantity in zip(product_ids, quantities):
        product = Producto.objects.get(id=product_id)
        item_total = float(product.precio) * int(quantity)
        total += item_total
        
        BudgetItem.objects.create(
            budget=budget,
            product=product,
            quantity=quantity,
            price=product.precio
        )
    return total

def _send_email_async(budget, pdf_buffer):
    def send():
        try:
            send_budget_email(budget, pdf_buffer)
        except Exception as e:
            logging.error(f"Error enviando email: {str(e)}")
    threading.Thread(target=send, daemon=True).start()