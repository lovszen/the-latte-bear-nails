from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from core.models import Budget, BudgetItem
from core.utils import generate_budget_pdf, send_budget_email
from .models import Producto
import mercadopago
from django.conf import settings
import json
import threading
import logging

try:
    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
except Exception as e:
    print(f"Error al inicializar el SDK de MercadoPago: {e}")
    sdk = None

# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/tienda.html', {'productos': productos})

def create_budget_from_cart(request):
    """
    View to create a budget from cart items
    """
    # Check for POST method first
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    # Manual authentication check 
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    try:
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

        # Generate PDF - with enhanced error handling
        try:
            pdf_buffer = generate_budget_pdf(budget)
        except Exception as pdf_error:
            logging.exception(f"Error generating budget PDF: {str(pdf_error)}")
            return JsonResponse({'success': False, 'error': f'Error generando PDF: {str(pdf_error)}'})

        # Try to send email, but don't let email failures crash the entire operation
        # Instead, return success immediately and send email in the background
        try:
            # Start email sending in a separate thread to avoid blocking
            def send_email_async():
                try:
                    email_sent = send_budget_email(budget, pdf_buffer)
                    if not email_sent:
                        logging.warning(f"Failed to send budget email for budget {budget.id}")
                except Exception as email_error:
                    logging.exception(f"Exception during async email sending for budget {budget.id}: {str(email_error)}")
            
            # Start the email sending in a daemon thread so it doesn't prevent shutdown
            email_thread = threading.Thread(target=send_email_async, daemon=True)
            email_thread.start()
            
            # Return success immediately without waiting for email to be sent
            return JsonResponse({'success': True, 'message': 'Presupuesto creado exitosamente'})
            
        except Exception as email_error:
            logging.exception(f"Unexpected error starting email thread: {str(email_error)}")
            # Still return success - email is not critical for the budget creation process
            return JsonResponse({'success': True, 'message': 'Presupuesto creado exitosamente (email pendiente de envío)'})

    except Producto.DoesNotExist:
        logging.exception("Producto not found in create_budget_from_cart")
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    except ValueError as e:
        logging.exception(f"Value error in create_budget_from_cart: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Error de formato en datos: {str(e)}'})
    except Exception as e:
        logging.exception(f"Unexpected error in create_budget_from_cart: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@login_required
@require_POST
def crear_pago_carrito_js(request):
    """
    Toma los datos del carrito (enviados por JS como JSON)
    y crea la preferencia de pago en MercadoPago.
    """
    if not sdk:
        print("!!!!!!!! ERROR GRAVE: SDK de MercadoPago no inicializado !!!!!")
        return JsonResponse({'error': 'El servicio de pago no está configurado.'}, status=500)

    try:
        # Parse the JSON data from the request body
        json_data = json.loads(request.body)

        # Extract cart items from the JSON data
        cart_items = json_data.get('items', [])

        # Check if there are items to process
        if not cart_items:
            return JsonResponse({'error': 'No hay productos para procesar'}, status=400)

        # Format items for MercadoPago
        items_para_mp = []
        for item in cart_items:
            # Get price - JavaScript sends 'unit_price' from item.precio
            price_raw = item.get('unit_price', 0)
            if isinstance(price_raw, (int, float)):
                unit_price = float(price_raw)
            else:
                # Handle string format, potentially in Argentine format
                price_str = str(price_raw).strip().replace('.', '').replace(',', '.')
                try:
                    unit_price = float(price_str)
                except ValueError:
                    unit_price = 0.0

            # Format to 2 decimal places as required by MercadoPago
            unit_price = round(unit_price, 2)

            # Ensure unit_price is positive and not zero
            if unit_price <= 0:
                print(f"DEBUG: Price was zero or negative ({unit_price}) for item {item.get('title', 'unknown')}, raw price was {item.get('unit_price', 0)}")
                unit_price = 0.01  # Minimum value to avoid error

            items_para_mp.append({
                "title": item.get('title', 'Producto'),
                "quantity": max(1, int(item.get('quantity', 1))),  # Ensure quantity is at least 1
                "unit_price": unit_price,
                "currency_id": "ARS"
            })

        # Prepare the preference data
        preference_data = {
            "items": items_para_mp,
            "back_urls": {
                "success": request.build_absolute_uri('/payment/success/'),
                "failure": request.build_absolute_uri('/payment/failure/'),
                "pending": request.build_absolute_uri('/payment/pending/')
            },
            "external_reference": f"cart_{request.user.id}_{request.session.session_key if hasattr(request, 'session') and request.session.session_key else 'no_session'}",
        }

        preference_response = sdk.preference().create(preference_data)


        print("====================================")
        print("===== RESPUESTA DE MERCADOPAGO =====")
        print(preference_response)
        print("====================================")


        if preference_response["status"] == 201:

            preference = preference_response["response"]
            return JsonResponse({'init_point': preference['init_point']})
        else:

            error_msg = preference_response["response"].get("message", "Error desconocido de MercadoPago")
            print(f"MercadoPago devolvió un error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

    except Exception as e:

        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"¡EL SERVIDOR CRASHEÓ! El error es: {e}")
        if 'preference_response' in locals():
            print("LA RESPUESTA (CON ERROR) FUE:")
            print(preference_response)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return JsonResponse({'error': str(e)}, status=500)