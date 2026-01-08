"""
Tenant model for multi-tenancy support.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Tenant(models.Model):
    """
    Tenant model for multi-tenancy.
    Each tenant represents an independent client/organization.
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    name = models.CharField(
        _('Tenant Name'),
        max_length=200,
        help_text=_('Name of the organization or client')
    )
    
    slug = models.SlugField(
        _('Slug'),
        max_length=100,
        unique=True,
        help_text=_('URL-friendly identifier')
    )
    
    domain = models.URLField(
        _('Domain'),
        unique=True,
        help_text=_('Primary domain for this tenant')
    )
    
    settings = models.JSONField(
        _('Settings'),
        default=dict,
        blank=True,
        help_text=_('Custom configuration for this tenant')
    )
    
    subscription_tier = models.CharField(
        _('Subscription Tier'),
        max_length=50,
        choices=[
            ('free', 'Free'),
            ('basic', 'Basic'),
            ('pro', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        default='basic'
    )
    
    max_properties = models.IntegerField(
        _('Max Properties'),
        default=100,
        help_text=_('Maximum number of properties allowed')
    )
    
    max_users = models.IntegerField(
        _('Max Users'),
        default=10,
        help_text=_('Maximum number of users allowed')
    )
    
    is_active = models.BooleanField(
        _('Active'),
        default=True,
        help_text=_('Is this tenant currently active?')
    )
    
    created_at = models.DateTimeField(
        _('Created At'),
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        _('Updated At'),
        auto_now=True
    )
    
    class Meta:
        db_table = 'tenants'
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.slug})"
    
    def get_property_count(self):
        """Get current number of properties for this tenant."""
        return self.property_set.filter(is_active=True).count()
    
    def get_user_count(self):
        """Get current number of users for this tenant."""
        return self.customuser_set.filter(is_active=True).count()
    
    def can_add_property(self):
        """Check if tenant can add more properties."""
        return self.get_property_count() < self.max_properties
    
    def can_add_user(self):
        """Check if tenant can add more users."""
        return self.get_user_count() < self.max_users
