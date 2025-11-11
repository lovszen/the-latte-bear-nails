from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import TelegramChatMessage
from .serializers import TelegramChatMessageSerializer, TelegramChatAdminReplySerializer
from .utils import enviar_a_telegram, enviar_imagen_a_telegram
import json
import cloudinary
import cloudinary.uploader


class TelegramChatCreateView(generics.CreateAPIView):
    queryset = TelegramChatMessage.objects.all()
    serializer_class = TelegramChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(
            sender_name=user.get_full_name() or user.username,
            sender_email=user.email,
            message_type='user'
        )
        
        if instance.image_url:  
            mensaje = (
                f"Nuevo mensaje de chat\n\n"
                f"Nombre: {instance.sender_name}\n"
                f"Email: {instance.sender_email}\n"
                f"Mensaje: {instance.message}"
            )
            enviar_a_telegram(mensaje)
            enviar_imagen_a_telegram(instance.image_url)  
        else:
            mensaje = (
                f"Nuevo mensaje de chat\n\n"
                f"Nombre: {instance.sender_name}\n"
                f"Email: {instance.sender_email}\n"
                f"Mensaje: {instance.message}"
            )
            enviar_a_telegram(mensaje)


class TelegramChatListView(generics.ListAPIView):
    """Endpoint to get all messages for a chat conversation"""
    serializer_class = TelegramChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_email = user.email
        
        actual_email = user_email or f"{user.username}@user-{user.id}.local"
        
        user_messages = TelegramChatMessage.objects.filter(sender_email=actual_email)
        admin_replies = TelegramChatMessage.objects.filter(original_message__sender_email=actual_email)
        
        all_messages = (user_messages | admin_replies).order_by('timestamp')
        
        return all_messages

@api_view(['GET'])
def get_my_messages(request):
    """API endpoint to get all messages for the authenticated user (user + admin replies)"""
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = request.user
    user_email = user.email
    
    actual_email = user_email or f"{user.username}@user-{user.id}.local"
    
    since_timestamp = request.GET.get('since', None)
    
    user_messages = TelegramChatMessage.objects.filter(sender_email=actual_email)
    admin_replies = TelegramChatMessage.objects.filter(original_message__sender_email=actual_email)

    if since_timestamp:
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        try:
            since_dt = parse_datetime(since_timestamp)
            if since_dt:
                if timezone.is_naive(since_dt):
                    since_dt = timezone.make_aware(since_dt)
                
                user_messages = user_messages.filter(timestamp__gt=since_dt)
                admin_replies = admin_replies.filter(timestamp__gt=since_dt)
        except Exception as e:
            print(f"Error parsing since_timestamp: {e}")
    
    all_messages = (user_messages | admin_replies).order_by('timestamp')
    
    serializer = TelegramChatMessageSerializer(all_messages, many=True, context={'request': request})
    return Response(serializer.data)


class TelegramChatAdminReplyView(generics.CreateAPIView):
    """Endpoint for admins to reply to user messages"""
    serializer_class = TelegramChatAdminReplySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def check_permissions(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            self.permission_denied(
                request, message='Only staff members can send admin replies.'
            )
        return super().check_permissions(request)

    def perform_create(self, serializer):
        admin_reply = serializer.save(
            admin_user=self.request.user,
            message_type='admin'
        )
        
        original_message = admin_reply.original_message
        original_sender = original_message.sender_name if original_message else "Usuario"
        
        mensaje = (
            f" respuesta del admin para {original_sender}\n\n"
            f"Mensaje de admin: {admin_reply.message}"
        )
        enviar_a_telegram(mensaje)


@api_view(['POST'])
def send_telegram_message(request):
    """API endpoint for sending messages to Telegram via web interface"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    sender_name = user.get_full_name() or user.username
    sender_email = user.email or f"{user.username}@user-{user.id}.local"
    message = request.data.get('message', '')
    image_url = request.data.get('image_url', '')

    if not message and not image_url:
        return Response(
            {'error': 'Message or image is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    image_to_save = None
    image_url_to_save = None

    if image_url and image_url.startswith('data:image'):
        try:
            result = cloudinary.uploader.upload(image_url, folder="chat_images")
            image_url_to_save = result['secure_url']
        except Exception as e:
            image_url_to_save = image_url
    else:
        image_url_to_save = image_url if image_url else None

    try:
        with transaction.atomic():
            chat_message = TelegramChatMessage.objects.create(
                sender_name=sender_name,
                sender_email=sender_email,
                message=message,
                image_url=image_url_to_save,
                message_type='user'
            )

            if image_url_to_save:
                mensaje = (
                    f"Nuevo mensaje de chat\n\n"
                    f"Nombre: {sender_name}\n"
                    f"Email: {sender_email}\n"
                    f"Mensaje: {message or 'Imagen sin texto'}"
                )
                enviar_a_telegram(mensaje)
                enviar_imagen_a_telegram(image_url_to_save)
            else:
                mensaje = (
                    f"Nuevo mensaje de chat\n\n"
                    f"Nombre: {sender_name}\n"
                    f"Email: {sender_email}\n"
                    f"Mensaje: {message}"
                )
                enviar_a_telegram(mensaje)

        serializer = TelegramChatMessageSerializer(chat_message, context={'request': request})
        return Response(
            {
                'success': True, 
                'message_id': chat_message.id,
                'saved_message': serializer.data
            }, 
            status=status.HTTP_201_CREATED
        )
    except Exception as e:
        print(f"Error saving chat message: {str(e)}")
        return Response(
            {'error': f'Failed to save message: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def admin_chat_view(request):
    """Admin view to manage chat messages and reply to users"""
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('home') 
    
    user_messages = TelegramChatMessage.objects.filter(
        message_type='user'
    ).order_by('-timestamp')
    
    conversations = {}
    for msg in user_messages:
        email = msg.sender_email
        if email not in conversations:
            conversations[email] = {
                'sender_name': msg.sender_name,
                'sender_email': email,
                'messages': []
            }
        conversations[email]['messages'].append(msg)
    
    return render(request, 'core/admin_chat.html', {
        'conversations': conversations.items()
    })


@api_view(['GET'])
def get_user_messages(request, email):
    """API endpoint to get all messages for a specific user email (user + admin replies)"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    

    since_timestamp = request.GET.get('since', None)
    
    user_messages = TelegramChatMessage.objects.filter(sender_email=email)
    admin_replies = TelegramChatMessage.objects.filter(original_message__sender_email=email)
    
    if since_timestamp:
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        
        try:
            since_dt = parse_datetime(since_timestamp)
            if since_dt:
                if timezone.is_naive(since_dt):
                    since_dt = timezone.make_aware(since_dt)
                
                user_messages = user_messages.filter(timestamp__gt=since_dt)
                admin_replies = admin_replies.filter(timestamp__gt=since_dt)
        except Exception as e:
            print(f"Error parsing since_timestamp: {e}")
    
    all_messages = (user_messages | admin_replies).order_by('timestamp')
    
    serializer = TelegramChatMessageSerializer(all_messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
def upload_image_to_cloudinary(request):
    """API endpoint to upload images to Cloudinary"""
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['image']
    
    if image.size > 2 * 1024 * 1024:
        return Response({'error': 'La imagen es demasiado grande. El tamaño máximo es de 2MB.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        result = cloudinary.uploader.upload(image, folder="chat_images")
        return Response({
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id']
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
