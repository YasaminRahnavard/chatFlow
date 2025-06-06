"""
Django Models for Chat Application
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Extended User model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_guest = models.BooleanField(default=False)
    guest_session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        if self.is_guest:
            return f"Guest User ({self.guest_session_id})"
        return f"{self.username} ({self.email})"


class Conversation(models.Model):
    """Chat Conversation model - supports both authenticated and guest users"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='conversations',
        null=True,
        blank=True
    )
    # For guest users - store session ID directly
    guest_session_id = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
        
    def __str__(self):
        if self.user and not self.user.is_guest:
            return f"{self.title} - {self.user.username}"
        elif self.user and self.user.is_guest:
            return f"{self.title} - Guest ({self.user.guest_session_id})"
        else:
            return f"{self.title} - Guest ({self.guest_session_id})"
    
    @property
    def message_count(self):
        return self.messages.count()
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()
    
    @property
    def is_guest_conversation(self):
        return (self.user and self.user.is_guest) or self.guest_session_id


class Message(models.Model):
    """Chat Message model"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    content = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Update conversation's updated_at when new message is added
        super().save(*args, **kwargs)
        self.conversation.updated_at = timezone.now()
        self.conversation.save(update_fields=['updated_at'])


class APIUsage(models.Model):
    """API Usage tracking model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='api_usage',
        null=True, 
        blank=True
    )
    # For guest users - store session ID directly
    guest_session_id = models.CharField(max_length=255, blank=True, null=True)
    endpoint = models.CharField(max_length=255)
    tokens_used = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_usage'
        ordering = ['-created_at']
        
    def __str__(self):
        if self.user and not self.user.is_guest:
            user_info = self.user.username
        elif self.user and self.user.is_guest:
            user_info = f'Guest ({self.user.guest_session_id})'
        else:
            user_info = f'Guest ({self.guest_session_id})'
        return f"{self.endpoint} - {user_info} - {self.tokens_used} tokens"
