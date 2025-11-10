from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Budget, BudgetItem
from .utils import generate_budget_pdf, send_budget_email
from productos.models import Producto
import threading
import logging

@login_required
def budgets_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'budgets/budgets_list.html', {'budgets': budgets})

@login_required
def view_budget(request, budget_id):
    budget = Budget.objects.get(id=budget_id, user=request.user)
    return render(request, 'budgets/view_budget.html', {'budget': budget})

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

# ========== HELPERS ==========
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