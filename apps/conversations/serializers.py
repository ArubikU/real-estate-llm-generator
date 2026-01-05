"""
Serializers for Conversations app.
"""

from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    sources = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'role', 'role_display', 'content',
            'tokens_input', 'tokens_output', 'model_used',
            'latency_ms', 'sources', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_sources(self, obj):
        """Get formatted sources."""
        return obj.get_sources()


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model."""
    
    message_count = serializers.IntegerField(source='get_message_count', read_only=True)
    last_message_at = serializers.DateTimeField(source='get_last_message_at', read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'tenant', 'user', 'user_role', 'title', 'summary',
            'total_tokens', 'total_cost_usd', 'is_archived',
            'message_count', 'last_message_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_tokens', 'total_cost_usd', 'created_at', 'updated_at']


class ConversationDetailSerializer(ConversationSerializer):
    """Detailed serializer with messages."""
    
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']
