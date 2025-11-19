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
        
        if contexto == 'tienda_uñas':
            prompt = f"""Eres un asistente especializado en uñas postizas y productos de belleza.

Usuario pregunta: "{user_message}"
Productos encontrados en la tienda: {productos_count}

Responde de forma amigable y útil, enfocada en uñas y belleza.
Máximo 2 líneas. Sé entusiasta."""
        else:
            prompt = user_message
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 150
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