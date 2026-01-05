from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ('role', 'content', 'model_used', 'tokens_input', 'tokens_output', 'created_at')
    readonly_fields = ('created_at',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'tenant', 'user_role', 'get_message_count', 
                    'total_tokens', 'is_archived', 'created_at', 'updated_at')
    list_filter = ('is_archived', 'user_role', 'tenant', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('id', 'total_tokens', 'total_cost_usd', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'user', 'user_role', 'title')
        }),
        ('Summary', {
            'fields': ('summary',)
        }),
        ('Usage & Cost', {
            'fields': ('total_tokens', 'total_cost_usd')
        }),
        ('Status', {
            'fields': ('is_archived', 'created_at', 'updated_at')
        }),
    )
    
    inlines = [MessageInline]
    
    actions = ['archive_conversations', 'unarchive_conversations', 'update_costs']
    
    def archive_conversations(self, request, queryset):
        queryset.update(is_archived=True)
        self.message_user(request, f"{queryset.count()} conversations archived.")
    archive_conversations.short_description = "Archive selected conversations"
    
    def unarchive_conversations(self, request, queryset):
        queryset.update(is_archived=False)
        self.message_user(request, f"{queryset.count()} conversations unarchived.")
    unarchive_conversations.short_description = "Unarchive selected conversations"
    
    def update_costs(self, request, queryset):
        for conv in queryset:
            conv.update_costs()
        self.message_user(request, f"Updated costs for {queryset.count()} conversations.")
    update_costs.short_description = "Update token costs"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'role', 'content_preview', 'model_used', 
                    'tokens_input', 'tokens_output', 'created_at')
    list_filter = ('role', 'model_used', 'created_at')
    search_fields = ('content', 'conversation__title')
    readonly_fields = ('id', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'conversation', 'role', 'content')
        }),
        ('Model & Tokens', {
            'fields': ('model_used', 'tokens_input', 'tokens_output', 'latency_ms')
        }),
        ('RAG Context', {
            'fields': ('retrieved_documents',),
            'classes': ('collapse',)
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
