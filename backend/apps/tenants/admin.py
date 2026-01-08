from django.contrib import admin
from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'subscription_tier', 'is_active', 'created_at')
    list_filter = ('is_active', 'subscription_tier', 'created_at')
    search_fields = ('name', 'slug', 'domain')
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'domain')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'max_properties', 'max_users')
        }),
        ('Settings', {
            'fields': ('settings', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
