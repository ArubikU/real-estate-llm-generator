"""
Custom User model with role-based access control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.tenants.models import Tenant


class UserRole:
    """User role constants."""
    BUYER = 'buyer'
    TOURIST = 'tourist'
    VENDOR = 'vendor'
    STAFF = 'staff'
    ADMIN = 'admin'
    
    CHOICES = [
        (BUYER, _('Buyer/Investor')),
        (TOURIST, _('Tourist/Guest')),
        (VENDOR, _('Vendor')),
        (STAFF, _('Staff/Property Manager')),
        (ADMIN, _('Administrator')),
    ]


class CustomUser(AbstractUser):
    """
    Custom user model with tenant association and role-based access.
    """
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name=_('Tenant'),
        help_text=_('Organization this user belongs to')
    )
    
    role = models.CharField(
        _('Role'),
        max_length=20,
        choices=UserRole.CHOICES,
        default=UserRole.BUYER,
        help_text=_('User role determines what information they can access')
    )
    
    preferences = models.JSONField(
        _('Preferences'),
        default=dict,
        blank=True,
        help_text=_('User-specific settings and preferences')
    )
    
    phone = models.CharField(
        _('Phone Number'),
        max_length=20,
        blank=True,
        null=True
    )
    
    language = models.CharField(
        _('Preferred Language'),
        max_length=10,
        choices=[
            ('en', 'English'),
            ('es', 'Español'),
        ],
        default='en'
    )
    
    timezone = models.CharField(
        _('Timezone'),
        max_length=50,
        default='America/Costa_Rica'
    )
    
    is_verified = models.BooleanField(
        _('Email Verified'),
        default=False,
        help_text=_('Has the user verified their email address?')
    )
    
    last_active = models.DateTimeField(
        _('Last Active'),
        auto_now=True,
        help_text=_('Last time user was active')
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
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['email']),
        ]
        unique_together = [('tenant', 'email')]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return user's full name."""
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.username
    
    def can_view_prices(self):
        """Check if user role allows viewing property prices."""
        return self.role in [UserRole.BUYER, UserRole.STAFF, UserRole.ADMIN]
    
    def can_view_financial_data(self):
        """Check if user can view financial information."""
        return self.role in [UserRole.BUYER, UserRole.ADMIN]
    
    def can_view_personal_data(self):
        """Check if user can view personal data of guests."""
        return self.role in [UserRole.STAFF, UserRole.ADMIN]
    
    def can_manage_properties(self):
        """Check if user can add/edit properties."""
        return self.role in [UserRole.STAFF, UserRole.ADMIN]
    
    def get_allowed_document_types(self):
        """Get document types this user role can access."""
        role_documents = {
            UserRole.BUYER: ['property', 'investment', 'legal', 'market'],
            UserRole.TOURIST: ['amenity', 'activity', 'restaurant', 'tour'],
            UserRole.VENDOR: ['demand', 'pricing', 'service'],
            UserRole.STAFF: ['sop', 'vendor', 'maintenance', 'guest'],
            UserRole.ADMIN: ['all'],
        }
        return role_documents.get(self.role, [])
