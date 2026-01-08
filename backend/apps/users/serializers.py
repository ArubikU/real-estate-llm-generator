"""
Serializers for Users app.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserRole


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tenant', 'tenant_name', 'role', 'role_display',
            'phone', 'language', 'timezone', 'preferences',
            'is_verified', 'is_active', 'last_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_active', 'created_at', 'updated_at']
        extra_kwargs = {
            'email': {'required': True}
        }


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'tenant', 'role'
        ]
    
    def validate(self, attrs):
        """Validate passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs
    
    def validate_tenant(self, value):
        """Validate tenant can add more users."""
        if not value.can_add_user():
            raise serializers.ValidationError("Tenant has reached maximum user limit")
        return value
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (more detailed)."""
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    can_view_prices = serializers.BooleanField(read_only=True)
    can_view_financial_data = serializers.BooleanField(read_only=True)
    can_manage_properties = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'tenant', 'tenant_name', 'role', 'role_display',
            'phone', 'language', 'timezone', 'preferences',
            'is_verified', 'last_active',
            'can_view_prices', 'can_view_financial_data', 'can_manage_properties',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tenant', 'last_active', 'created_at', 'updated_at']
