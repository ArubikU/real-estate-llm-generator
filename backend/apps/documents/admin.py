from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'tenant', 'content_type', 'user_roles', 'times_retrieved', 
                    'is_active', 'freshness_date', 'created_at')
    list_filter = ('is_active', 'content_type', 'tenant', 'freshness_date', 'created_at')
    search_fields = ('content', 'source_reference')
    readonly_fields = ('id', 'times_retrieved', 'avg_relevance_score', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tenant', 'content', 'content_type')
        }),
        ('Access Control', {
            'fields': ('user_roles',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'source_url', 'source_reference', 'freshness_date')
        }),
        ('Analytics', {
            'fields': ('times_retrieved', 'avg_relevance_score')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    actions = ['mark_as_inactive', 'mark_as_active']
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} documents marked as inactive.")
    mark_as_inactive.short_description = "Mark as inactive"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} documents marked as active.")
    mark_as_active.short_description = "Mark as active"
