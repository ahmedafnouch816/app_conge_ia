from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import classify_message

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            # Récupérer les données envoyées en JSON
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()

            if not user_message:
                return JsonResponse({'error': 'Message vide non autorisé'}, status=400)

            # Obtenir la réponse du chatbot
            bot_response = classify_message(user_message)
            return JsonResponse({'response': bot_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Format JSON invalide'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)