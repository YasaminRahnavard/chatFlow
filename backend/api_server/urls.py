"""
URL Configuration for Docker Chat Platform API Server
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health_check(request):
    """Health check endpoint for Docker containers"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'api-server',
        'version': '1.0.0'
    })

def api_root(request):
    """API root endpoint with available endpoints"""
    return JsonResponse({
        'message': 'Welcome to Docker Chat Platform API!',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'chat': '/api/chat/',
            'auth': '/api/auth/',
            'health': '/health/',
            'docs': '/api/docs/',
        }
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API root
    path('', api_root, name='api_root'),
    
    # Chat application URLs
    path('api/chat/', include('chat.urls')),
    
    # Authentication (future implementation)
    # path('api/auth/', include('auth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
