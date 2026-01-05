"""
Serializers for Documents app.
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model."""
    
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    is_fresh = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'tenant', 'content', 'user_roles', 'content_type', 'content_type_display',
            'freshness_date', 'source_url', 'source_reference', 'is_active',
            'times_retrieved', 'avg_relevance_score', 'is_fresh',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'times_retrieved', 'avg_relevance_score', 'created_at', 'updated_at']
    
    def get_is_fresh(self, obj):
        """Check if document is fresh."""
        return obj.is_fresh()

