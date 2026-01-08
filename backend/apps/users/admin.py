from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'tenant', 'role', 'is_active', 'is_verified', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'role', 'tenant', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Tenant & Role', {
            'fields': ('tenant', 'role', 'preferences')
        }),
        ('Contact & Preferences', {
            'fields': ('phone', 'language', 'timezone')
        }),
        ('Verification', {
            'fields': ('is_verified', 'last_active')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('tenant', 'role', 'email', 'first_name', 'last_name')
        }),
    )
    
    readonly_fields = ('last_active', 'created_at', 'updated_at')
