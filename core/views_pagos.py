from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Budget
from productos.models import Producto
import mercadopago
from django.conf import settings
import json

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN) if hasattr(settings, 'MERCADOPAGO_ACCESS_TOKEN') else None

@login_required
@require_POST
def crear_pago_carrito_js(request):
    return _handle_mercado_pago(request, from_cart=True)

@login_required
def crear_pago_presupuesto(request, budget_id):
    return _handle_mercado_pago(request, budget_id=budget_id)

@login_required
def mp_create_payment(request, budget_id):
    return _handle_mercado_pago(request, budget_id=budget_id)

def _handle_mercado_pago(request, from_cart=False, budget_id=None):
    if not sdk:
        return JsonResponse({'error': 'Servicio no configurado'}, status=500) if from_cart else redirect('budgets_list')
    
    try:
        if from_cart:
            cart_items = json.loads(request.body).get('items', [])
            if not cart_items:
                return JsonResponse({'error': 'Carrito vacío'}, status=400)
            items_para_mp = _format_cart_items(cart_items)
        else:
            budget = Budget.objects.get(id=budget_id, user=request.user)
            if not budget.items.exists():
                return redirect('view_budget', budget_id=budget.id)
            items_para_mp = _format_budget_items(budget)
        
        preference_data = {
            "items": items_para_mp,
            "back_urls": {
                "success": request.build_absolute_uri('/payment/success/'),
                "failure": request.build_absolute_uri('/payment/failure/'),
                "pending": request.build_absolute_uri('/payment/pending/')
            }
        }
        
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            init_point = preference_response["response"]['init_point']
            return JsonResponse({'init_point': init_point}) if from_cart else redirect(init_point)
        return JsonResponse({'error': 'Error en MercadoPago'}, status=400) if from_cart else redirect('budgets_list')
            
    except Exception as e:
        error_msg = 'Error interno del servidor'
        return JsonResponse({'error': error_msg}, status=500) if from_cart else redirect('budgets_list')

def _format_cart_items(cart_items):
    return [{
        "title": item.get('title', 'Producto'),
        "quantity": max(1, int(item.get('quantity', 1))),
        "unit_price": round(float(str(item.get('unit_price', 0)).replace('.', '').replace(',', '.')), 2),
        "currency_id": "ARS"
    } for item in cart_items]

def _format_budget_items(budget):
    return [{
        "title": item.product.nombre,
        "quantity": max(1, int(item.quantity)),
        "unit_price": round(float(item.price), 2),
        "currency_id": "ARS"
    } for item in budget.items.all()]