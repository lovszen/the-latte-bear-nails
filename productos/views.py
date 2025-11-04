from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.models import Budget, BudgetItem
from core.utils import generate_budget_pdf, send_budget_email
from .models import Producto

# Create your views here.

def lista_productos(request): 
    productos = Producto.objects.all()
    return render(request, 'productos/tienda.html', {'productos': productos})

@login_required
@require_http_methods(["POST"])
def create_budget_from_cart(request):
    """
    View to create a budget from cart items
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        customer_name = request.POST.get('customer_name')
        
        # Always send to the logged-in user's email (no customer email input)
        customer_email = request.user.email
        
        # If customer name is not provided, use the user's username
        if not customer_name or customer_name == '':
            customer_name = request.user.username
        
        # Handle both comma-separated strings and multiple inputs
        product_ids_raw = request.POST.getlist('product_ids')
        quantities_raw = request.POST.getlist('quantities')
        
        # Parse product_ids: handle both list format and comma-separated string format
        product_ids = []
        for pid in product_ids_raw:
            if ',' in pid:
                # Split comma-separated string
                product_ids.extend([int(id.strip()) for id in pid.split(',') if id.strip().isdigit()])
            else:
                # Single ID
                if pid.isdigit():
                    product_ids.append(int(pid))
        
        # Parse quantities: handle both list format and comma-separated string format
        quantities = []
        for qty in quantities_raw:
            if ',' in qty:
                # Split comma-separated string
                quantities.extend([int(q.strip()) for q in qty.split(',') if q.strip().isdigit()])
            else:
                # Single quantity
                if qty.isdigit():
                    quantities.append(int(qty))
        
        try:
            # Validate required fields
            if not title:
                return JsonResponse({'success': False, 'error': 'Falta el título del presupuesto'})
            
            if not customer_name or not customer_email:
                return JsonResponse({'success': False, 'error': 'Faltan los datos del cliente'})
            
            if not product_ids or not quantities:
                return JsonResponse({'success': False, 'error': 'No hay productos en el presupuesto'})
            
            # Verify that we have matching number of products and quantities
            if len(product_ids) != len(quantities):
                return JsonResponse({'success': False, 'error': 'La cantidad de productos y cantidades no coincide'})
            
            # Create the budget
            budget = Budget.objects.create(
                user=request.user,
                title=title,
                customer_name=customer_name,
                customer_email=customer_email,
                total_amount=0  # Will calculate after adding items
            )
            
            # Add items to the budget
            total = 0
            for i, product_id in enumerate(product_ids):
                if i < len(quantities):
                    product = Producto.objects.get(id=product_id)
                    quantity = int(quantities[i])
                    price = float(product.precio)  # Convert to float for calculation
                    item_total = price * quantity
                    total += item_total
                    
                    BudgetItem.objects.create(
                        budget=budget,
                        product=product,
                        quantity=quantity,
                        price=price
                    )
            
            # Update total amount
            budget.total_amount = total
            budget.save()
            
            # Generate PDF and send via email
            pdf_buffer = generate_budget_pdf(budget)
            email_sent = send_budget_email(budget, pdf_buffer)
            
            # Always return JSON response since this will only be called via AJAX
            if email_sent:
                return JsonResponse({'success': True, 'message': 'Presupuesto creado y enviado exitosamente'})
            else:
                return JsonResponse({'success': False, 'error': 'Error al enviar el email'})
        
        except Producto.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
        except ValueError as e:
            return JsonResponse({'success': False, 'error': f'Error de formato en datos: {str(e)}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})