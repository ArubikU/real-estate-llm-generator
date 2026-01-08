"""
Views for Documents API.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Document
from .serializers import DocumentSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document management.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['content_type', 'is_active']
    search_fields = ['content', 'source_reference']
    
    def get_queryset(self):
        """Filter documents by tenant."""
        return Document.objects.filter(
            tenant=self.request.user.tenant
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set tenant on create."""
        serializer.save(tenant=self.request.user.tenant)
