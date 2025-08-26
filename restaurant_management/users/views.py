"""
Views para la API de usuarios.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """Registro de nuevos usuarios."""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login de usuarios."""
    serializer = UserLoginSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'Login exitoso',
            'user': UserProfileSerializer(user).data,
            'token': token.key
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout de usuarios."""
    try:
        # Eliminar token
        Token.objects.filter(user=request.user).delete()
        logout(request)
        
        return Response({
            'message': 'Logout exitoso'
        })
    except Exception:
        return Response({
            'error': 'Error durante logout'
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveAPIView):
    """Vista para obtener perfil del usuario autenticado."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.UpdateAPIView):
    """Vista para actualizar perfil del usuario."""
    
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    """Cambio de contraseña."""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        
        # Invalidar tokens existentes creando uno nuevo
        Token.objects.filter(user=request.user).delete()
        token = Token.objects.create(user=request.user)
        
        return Response({
            'message': 'Contraseña cambiada exitosamente',
            'token': token.key
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
