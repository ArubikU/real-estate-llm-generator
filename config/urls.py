"""
URL configuration for Real Estate LLM project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.utils.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),
    
    # Sin /api/ prefix
    path('v1/auth/', include('apps.users.urls')),
    path('v1/tenants/', include('apps.tenants.urls')),
    path('v1/properties/', include('apps.properties.urls')),
    path('v1/documents/', include('apps.documents.urls')),
    path('v1/conversations/', include('apps.conversations.urls')),
    path('v1/chat/', include('apps.chat.urls')),
    path('v1/ingest/', include('apps.ingestion.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # In production, serve static files from staticfiles directory
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
