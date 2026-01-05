"""
Views for Conversations API.
"""

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Conversation
from .serializers import ConversationSerializer, ConversationDetailSerializer


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Conversation management.
    Read-only as conversations are created through chat endpoint.
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_archived', 'user_role']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Filter conversations by user."""
        return Conversation.objects.filter(
            user=self.request.user,
            tenant=self.request.user.tenant
        ).prefetch_related('messages')
    
    def get_serializer_class(self):
        """Return detailed serializer for retrieve."""
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
