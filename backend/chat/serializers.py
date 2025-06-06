"""
Django REST Framework Serializers for Chat Application
"""
from rest_framework import serializers
from .models import User, Conversation, Message, APIUsage


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 
            'last_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MessageSerializer(serializers.ModelSerializer):
    """Message serializer"""
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'content', 'role', 
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_role(self, value):
        """Validate message role"""
        if value not in ['user', 'assistant', 'system']:
            raise serializers.ValidationError("Role must be 'user', 'assistant', or 'system'")
        return value


class ConversationSerializer(serializers.ModelSerializer):
    """Conversation serializer"""
    messages = MessageSerializer(many=True, read_only=True)
    message_count = serializers.ReadOnlyField()
    last_message = MessageSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'title', 'created_at', 'updated_at',
            'messages', 'message_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class ConversationListSerializer(serializers.ModelSerializer):
    """Conversation list serializer (without messages for performance)"""
    message_count = serializers.ReadOnlyField()
    last_message = MessageSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'user', 'title', 'created_at', 'updated_at',
            'message_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']


class ChatRequestSerializer(serializers.Serializer):
    """Chat request serializer for AI interactions"""
    message = serializers.CharField(max_length=2000)
    conversation_id = serializers.UUIDField(required=False, allow_null=True)
    temperature = serializers.FloatField(min_value=0.0, max_value=2.0, default=0.7)
    max_tokens = serializers.IntegerField(min_value=1, max_value=4000, default=1000)
    
    def validate_message(self, value):
        """Validate message content"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Chat response serializer"""
    conversation_id = serializers.UUIDField()
    user_message = MessageSerializer()
    assistant_message = MessageSerializer()
    tokens_used = serializers.IntegerField()
    response_time_ms = serializers.IntegerField()


class APIUsageSerializer(serializers.ModelSerializer):
    """API Usage serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = APIUsage
        fields = [
            'id', 'user', 'endpoint', 'tokens_used', 
            'response_time_ms', 'status_code', 'created_at'
        ]
        read_only_fields = ['id', 'created_at'] 