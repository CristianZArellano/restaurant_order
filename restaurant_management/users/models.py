"""
Modelo de usuario personalizado para el sistema de gestión de restaurantes.
Refactorizado aplicando principios SOLID y LEAN Code.
"""
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.validators import PhoneNumberValidator
from core.models import TimestampedModel


class CustomUser(AbstractUser, TimestampedModel):
    """
    Usuario personalizado que extiende AbstractUser con funcionalidades adicionales.
    
    Attributes:
        phone (str): Número telefónico internacional opcional
        is_verified (bool): Estado de verificación de la cuenta
    """
    
    phone = models.CharField(
        validators=[PhoneNumberValidator()],
        max_length=16,
        blank=True,
        verbose_name=_("Teléfono"),
        help_text=_("Número telefónico en formato internacional")
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_("Verificado"),
        help_text=_("Indica si la cuenta del usuario ha sido verificada")
    )

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        """Representación string del usuario."""
        if self.email and self.get_full_name():
            return f"{self.get_full_name()} ({self.email})"
        elif self.email:
            return f"{self.username} ({self.email})"
        return self.username
    
    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        
        # Validar que el email sea único si se proporciona
        if self.email:
            existing = CustomUser.objects.filter(
                email__iexact=self.email
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'email': _("A user with this email already exists.")
                })
    
    def get_display_name(self):
        """Retorna el nombre para mostrar del usuario."""
        return self.get_full_name() or self.username
    
    @property
    def restaurants_count(self):
        """Número de restaurantes del usuario."""
        return self.restaurants.filter(is_active=True).count()
    
    @property
    def orders_count(self):
        """Número total de órdenes del usuario."""
        return self.orders.count()
    
    @property
    def has_restaurants(self):
        """Verifica si el usuario tiene restaurantes."""
        return self.restaurants.filter(is_active=True).exists()
