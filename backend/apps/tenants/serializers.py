"""
Serializers for Tenants app.
"""

from rest_framework import serializers
from .models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """Serializer for Tenant model."""
    
    property_count = serializers.IntegerField(source='get_property_count', read_only=True)
    user_count = serializers.IntegerField(source='get_user_count', read_only=True)
    can_add_property = serializers.BooleanField(source='can_add_property', read_only=True)
    can_add_user = serializers.BooleanField(source='can_add_user', read_only=True)
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'domain', 'settings',
            'subscription_tier', 'max_properties', 'max_users',
            'property_count', 'user_count', 'can_add_property', 'can_add_user',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
