"""
Serializers base para la API REST.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para usuario (sin información sensible)."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'display_name', 'is_verified']
        read_only_fields = ['id', 'is_verified']


class TimestampedSerializer(serializers.ModelSerializer):
    """Mixin para serializers con timestamps."""
    
    created_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M:%S')