"""
Django REST Framework Views for Chat Application
"""
import time
import uuid
import requests
from django.conf import settings
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, APIUsage, User
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    MessageSerializer, ChatRequestSerializer, ChatResponseSerializer,
    APIUsageSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class ConversationViewSet(viewsets.ModelViewSet):
    """Conversation management ViewSet"""
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """Get conversations for both authenticated and guest users"""
        # Handle guest users with session-based identification
        if not self.request.user or not self.request.user.is_authenticated:
            # Guest user - use session ID
            session_id = self.get_or_create_guest_session()
            return Conversation.objects.filter(guest_session_id=session_id)
        else:
            # Authenticated user
            return Conversation.objects.filter(user=self.request.user)
    
    def get_or_create_guest_session(self):
        """Get or create a guest session ID"""
        if not self.request.session.session_key:
            self.request.session.create()
        
        session_id = self.request.session.get('guest_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            self.request.session['guest_session_id'] = session_id
            self.request.session.save()
        
        return session_id
    
    def perform_create(self, serializer):
        """Create conversation for authenticated or guest user"""
        if self.request.user and self.request.user.is_authenticated:
            # Authenticated user
            serializer.save(user=self.request.user)
        else:
            # Guest user
            session_id = self.get_or_create_guest_session()
            serializer.save(guest_session_id=session_id)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a specific conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Send a message and get AI response - supports both authenticated and guest users"""
        start_time = time.time()
        
        # Validate request data
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        message_content = validated_data['message']
        conversation_id = validated_data.get('conversation_id')
        temperature = validated_data.get('temperature', 0.7)
        max_tokens = validated_data.get('max_tokens', 1000)
        
        # Handle user identification (authenticated or guest)
        user = None
        guest_session_id = None
        
        if request.user and request.user.is_authenticated:
            user = request.user
        else:
            guest_session_id = self.get_or_create_guest_session()
        
        # Get or create conversation
        if conversation_id:
            if user:
                conversation = get_object_or_404(Conversation, id=conversation_id, user=user)
            else:
                conversation = get_object_or_404(Conversation, id=conversation_id, guest_session_id=guest_session_id)
        else:
            # Create new conversation
            conversation_data = {
                'title': message_content[:50] + "..." if len(message_content) > 50 else message_content
            }
            if user:
                conversation_data['user'] = user
            else:
                conversation_data['guest_session_id'] = guest_session_id
            
            conversation = Conversation.objects.create(**conversation_data)
        
        # Create user message
        user_message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            role='user'
        )
        
        try:
            # Call AI service
            ai_response = self._call_ai_service(
                message_content, 
                conversation, 
                temperature, 
                max_tokens
            )
            
            # Create assistant message
            assistant_message = Message.objects.create(
                conversation=conversation,
                content=ai_response['content'],
                role='assistant',
                metadata={
                    'tokens_used': ai_response.get('tokens_used', 0),
                    'model': ai_response.get('model', 'gemini'),
                    'temperature': temperature,
                    'max_tokens': max_tokens
                }
            )
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Log API usage
            usage_data = {
                'endpoint': 'chat',
                'tokens_used': ai_response.get('tokens_used', 0),
                'response_time_ms': response_time_ms,
                'status_code': 200
            }
            if user:
                usage_data['user'] = user
            else:
                usage_data['guest_session_id'] = guest_session_id
            
            APIUsage.objects.create(**usage_data)
            
            # Prepare response
            response_data = {
                'conversation_id': conversation.id,
                'user_message': MessageSerializer(user_message).data,
                'assistant_message': MessageSerializer(assistant_message).data,
                'tokens_used': ai_response.get('tokens_used', 0),
                'response_time_ms': response_time_ms,
                'is_guest': user is None
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log error
            response_time_ms = int((time.time() - start_time) * 1000)
            usage_data = {
                'endpoint': 'chat',
                'tokens_used': 0,
                'response_time_ms': response_time_ms,
                'status_code': 500
            }
            if user:
                usage_data['user'] = user
            else:
                usage_data['guest_session_id'] = guest_session_id
            
            APIUsage.objects.create(**usage_data)
            
            return Response(
                {'error': f'AI service error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _call_ai_service(self, message, conversation, temperature=0.7, max_tokens=1000):
        """Call the AI service to get response"""
        # Get conversation history
        messages = list(conversation.messages.order_by('created_at').values('content', 'role'))
        
        # Prepare request to AI service
        ai_service_url = 'http://chatflow-ai:8001/chat'  # Updated container name
        payload = {
            'message': message,
            'conversation_history': messages[:-1],  # Exclude the just-created user message
            'temperature': temperature,
            'max_tokens': max_tokens
        }
        
        # Make request to AI service
        response = requests.post(
            ai_service_url,
            json=payload,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"AI service returned status {response.status_code}: {response.text}")


@method_decorator(csrf_exempt, name='dispatch')
class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """Message management ViewSet (read-only)"""
    serializer_class = MessageSerializer
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    
    def get_queryset(self):
        """Get messages for both authenticated and guest users"""
        if self.request.user and self.request.user.is_authenticated:
            # Authenticated user
            return Message.objects.filter(conversation__user=self.request.user)
        else:
            # Guest user
            if not self.request.session.session_key:
                return Message.objects.none()
            
            session_id = self.request.session.get('guest_session_id')
            if not session_id:
                return Message.objects.none()
            
            return Message.objects.filter(conversation__guest_session_id=session_id)


@method_decorator(csrf_exempt, name='dispatch')
class APIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """API Usage tracking ViewSet (read-only)"""
    serializer_class = APIUsageSerializer
    permission_classes = [AllowAny]  # Allow both authenticated and guest users
    
    def get_queryset(self):
        """Get API usage for both authenticated and guest users"""
        if self.request.user and self.request.user.is_authenticated:
            return APIUsage.objects.filter(user=self.request.user)
        else:
            # Guest user
            if not self.request.session.session_key:
                return APIUsage.objects.none()
            
            session_id = self.request.session.get('guest_session_id')
            if not session_id:
                return APIUsage.objects.none()
            
            return APIUsage.objects.filter(guest_session_id=session_id)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get usage statistics"""
        queryset = self.get_queryset()
        total_requests = queryset.count()
        total_tokens = queryset.aggregate(total=models.Sum('tokens_used'))['total'] or 0
        avg_response_time = queryset.aggregate(avg=models.Avg('response_time_ms'))['avg'] or 0
        
        return Response({
            'total_requests': total_requests,
            'total_tokens_used': total_tokens,
            'average_response_time_ms': round(avg_response_time, 2),
            'is_guest': not (request.user and request.user.is_authenticated)
        })


# Health check view
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for Docker"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-server',
        'version': '1.0.0',
        'app_name': 'ChatFlow'
    })
