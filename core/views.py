from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import mercadopago
from django.conf import settings
from .models import Budget, BudgetItem
from .utils import generate_budget_pdf, send_budget_email
from productos.models import Producto

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

def home(request):
    return render(request, 'home.html')

def lista_productos(request):
    return render(request, 'lista_productos.html')

@login_required
@require_http_methods(["POST"])
def generate_and_send_budget(request):
    """
    View to generate a budget PDF and send it via email
    """
    try:
        # Get data from request
        budget_id = request.POST.get('budget_id')
        if not budget_id:
            return JsonResponse({'error': 'Budget ID is required'}, status=400)
        
        # Get the budget
        budget = Budget.objects.get(id=budget_id, user=request.user)
        
        # Generate PDF
        pdf_buffer = generate_budget_pdf(budget)
        
        # Send email with PDF
        email_sent = send_budget_email(budget, pdf_buffer)
        
        if email_sent:
            return JsonResponse({'message': 'Presupuesto enviado correctamente'})
        else:
            return JsonResponse({'error': 'Error al enviar el presupuesto por email'}, status=500)
    
    except Budget.DoesNotExist:
        return JsonResponse({'error': 'Budget not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def download_budget_pdf(request, budget_id):
    """
    View to download the budget PDF
    """
    try:
        budget = Budget.objects.get(id=budget_id, user=request.user)
        pdf_buffer = generate_budget_pdf(budget)
        
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="presupuesto_{budget.id}.pdf"'
        return response
    
    except Budget.DoesNotExist:
        return HttpResponse('Budget not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)

@login_required
def create_budget(request):
    """
    View to create a new budget
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        
        try:
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
            
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                # If it's an AJAX request, return JSON response
                if email_sent:
                    return JsonResponse({'success': True, 'message': 'Presupuesto creado y enviado exitosamente'})
                else:
                    return JsonResponse({'success': False, 'error': 'Error al enviar el email'})
            else:
                # If it's a regular request, redirect to view budget
                messages.success(request, 'Presupuesto creado exitosamente')
                return redirect('view_budget', budget_id=budget.id)
        
        except Exception as e:
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f'Error al crear presupuesto: {str(e)}')
                return redirect('create_budget')
    
    # GET request - show available products
    products = Producto.objects.all()
    return render(request, 'budgets/create_budget.html', {'products': products})

@login_required
def view_budget(request, budget_id):
    """
    View to display a budget
    """
    budget = Budget.objects.get(id=budget_id, user=request.user)
    return render(request, 'budgets/view_budget.html', {'budget': budget})

@login_required
def edit_budget(request, budget_id):
    """
    View to edit an existing budget
    """
    budget = Budget.objects.get(id=budget_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        product_ids = request.POST.getlist('product_ids')
        quantities = request.POST.getlist('quantities')
        
        # Update budget details
        budget.title = title
        budget.customer_name = customer_name
        budget.customer_email = customer_email
        
        # Clear existing items
        budget.items.all().delete()
        
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
        
        messages.success(request, 'Presupuesto actualizado exitosamente')
        return redirect('view_budget', budget_id=budget.id)
    
    # GET request - show budget with available products
    products = Producto.objects.all()
    return render(request, 'budgets/edit_budget.html', {'budget': budget, 'products': products})

@login_required
def delete_budget(request, budget_id):
    """
    View to delete a budget
    """
    budget = Budget.objects.get(id=budget_id, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Presupuesto eliminado exitosamente')
        return redirect('budgets_list')
    
    return render(request, 'budgets/delete_budget.html', {'budget': budget})

@login_required
def budgets_list(request):
    """
    View to list all budgets for the user
    """
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'budgets/budgets_list.html', {'budgets': budgets})

@login_required
def crear_pago_presupuesto(request, budget_id):
    """
   
    """
    try:
        
        budget = Budget.objects.get(id=budget_id, user=request.user)
    except Budget.DoesNotExist:
        messages.error(request, "El presupuesto no existe.")
        return redirect('budgets_list') 

    
    # Check if the budget has items
    if not budget.items.exists():
        messages.error(request, "El presupuesto no tiene productos.")
        return redirect('view_budget', budget_id=budget.id)
    
    items_para_mp = []
    for item in budget.items.all(): 
        unit_price = round(float(item.price), 2)
        # Ensure unit_price is positive and not zero
        if unit_price <= 0:
            unit_price = 0.01  # Minimum value to avoid error
        
        items_para_mp.append({
            "title": item.product.nombre,
            "quantity": max(1, int(item.quantity)),  # Ensure quantity is at least 1
            "unit_price": unit_price, 
            "currency_id": "ARS" 
        })

    
    preference_data = {
        "items": items_para_mp,
        
        
        "back_urls": {
            "success": request.build_absolute_uri('/payment/success/'), 
            "failure": request.build_absolute_uri('/payment/failure/'),
            "pending": request.build_absolute_uri('/payment/pending/')
        },
        
        
        "external_reference": budget.id, 
    }

    try:
        
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        
        return redirect(preference["init_point"])

    except Exception as e:
        messages.error(request, f"Error al contactar con MercadoPago: {e}")
        return redirect('view_budget', budget_id=budget.id)



def payment_success(request):
    """
    Página a la que vuelve el usuario si el pago fue exitoso.
    """
    return render(request, 'payment_success.html')

def payment_failure(request):
    """
    Página a la que vuelve el usuario si el pago falla.
    """
    return render(request, 'payment_failure.html')

def payment_pending(request):
    """
    Página a la que vuelve el usuario si el pago queda pendiente.
    """
    return render(request, 'payment_pending.html')