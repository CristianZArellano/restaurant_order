"""
Serializers para la API de usuarios.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from core.serializers import TimestampedSerializer

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuarios."""
    
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone'
        ]
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        """Validación de contraseñas."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    
    def create(self, validated_data):
        """Crear nuevo usuario."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer para login de usuarios."""
    
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validar credenciales."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir username y password.',
                code='authorization'
            )


class UserProfileSerializer(TimestampedSerializer):
    """Serializer para el perfil del usuario."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    display_name = serializers.CharField(source='get_display_name', read_only=True)
    restaurants_count = serializers.IntegerField(read_only=True)
    orders_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'is_verified', 'full_name', 'display_name',
            'restaurants_count', 'orders_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'username', 'is_verified', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar perfil de usuario."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email']
        
    def validate_email(self, value):
        """Validar que el email no esté en uso por otro usuario."""
        user = self.instance
        if User.objects.filter(email__iexact=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Este email ya está en uso.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña."""
    
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validar contraseña actual."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta.")
        return value
    
    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Las nuevas contraseñas no coinciden.")
        return attrs
    
    def save(self):
        """Cambiar contraseña."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user