"""
Views for Tenants API.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Tenant
from .serializers import TenantSerializer


class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Tenant information.
    Read-only for regular users, admin can manage.
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer
    
    def get_queryset(self):
        """Filter tenants based on user permissions."""
        user = self.request.user
        
        if user.is_staff or user.is_superuser:
            return Tenant.objects.all()
        
        # Regular users can only see their own tenant
        return Tenant.objects.filter(id=user.tenant_id)
    
    @action(detail=True, methods=['get'], url_path='usage')
    def usage(self, request, pk=None):
        """Get detailed usage statistics for tenant."""
        tenant = self.get_object()
        
        # Check permission
        if request.user.tenant_id != tenant.id and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from apps.properties.models import Property
        from apps.users.models import CustomUser
        from apps.conversations.models import Conversation
        from django.db.models import Sum
        
        stats = {
            'properties': {
                'total': Property.objects.filter(tenant=tenant, is_active=True).count(),
                'limit': tenant.max_properties,
                'percentage': (Property.objects.filter(tenant=tenant, is_active=True).count() / tenant.max_properties * 100) if tenant.max_properties > 0 else 0
            },
            'users': {
                'total': CustomUser.objects.filter(tenant=tenant, is_active=True).count(),
                'limit': tenant.max_users,
                'percentage': (CustomUser.objects.filter(tenant=tenant, is_active=True).count() / tenant.max_users * 100) if tenant.max_users > 0 else 0
            },
            'conversations': {
                'total': Conversation.objects.filter(tenant=tenant).count(),
                'total_tokens': Conversation.objects.filter(tenant=tenant).aggregate(Sum('total_tokens'))['total_tokens__sum'] or 0,
                'total_cost_usd': float(Conversation.objects.filter(tenant=tenant).aggregate(Sum('total_cost_usd'))['total_cost_usd__sum'] or 0)
            }
        }
        
        return Response(stats, status=status.HTTP_200_OK)
