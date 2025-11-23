import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def gemini_proxy(request):
    try:
        data = json.loads(request.body)
        user_message = data.get('message')
        productos_count = data.get('productos_encontrados', 0)
        contexto = data.get('contexto', 'general')
        
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)
        
        if contexto == 'analisis_busqueda':
            prompt = f"""Eres un asistente de The Latte Bear Nails, tienda de uñas postizas.

{user_message}

Analiza la consulta del usuario y encuentra productos que coincidan FLEXIBLEMENTE.
Busca sinónimos y palabras relacionadas.

Responde EXCLUSIVAMENTE en este formato:
PRODUCTOS_COINCIDENTES: [nombres de productos separados por coma]
RESPUESTA: [respuesta amigable mencionando los productos encontrados]

Ejemplo:
PRODUCTOS_COINCIDENTES: Set Almendra Floral, Set Coffin Rosa
RESPUESTA: ¡Encontré estos sets preciosos para ti! Tenemos diseños florales y colores rosados que te encantarán 💅"""
        else:
            prompt = user_message
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 500
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200:
            gemini_response = response_data['candidates'][0]['content']['parts'][0]['text']
            return JsonResponse({'response': gemini_response})
        else:
            return JsonResponse({'error': 'Error from Gemini API'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)