"""
URL Configuration for Chat Application
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, APIUsageViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'usage', APIUsageViewSet, basename='apiusage')

app_name = 'chat'

urlpatterns = [
    # REST API endpoints
    path('', include(router.urls)),
] 