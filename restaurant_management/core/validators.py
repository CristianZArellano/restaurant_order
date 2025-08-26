"""
Validadores reutilizables para el sistema de gestión de restaurantes.
Aplicando principio DRY y Single Responsibility.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator(RegexValidator):
    """Validador reutilizable para números telefónicos internacionales."""
    
    regex = r"^\+?\d{7,15}$"
    message = _("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    code = "invalid_phone"


def validate_positive_decimal(value):
    """Valida que un decimal sea positivo."""
    if value <= Decimal('0'):
        raise ValidationError(_('Value must be greater than 0.'))


def validate_rating(value):
    """Valida que una calificación esté entre 1 y 5."""
    if not 1 <= value <= 5:
        raise ValidationError(_('Rating must be between 1 and 5.'))


def validate_preparation_time(value):
    """Valida que el tiempo de preparación sea razonable."""
    if not 1 <= value <= 300:  # Entre 1 minuto y 5 horas
        raise ValidationError(_('Preparation time must be between 1 and 300 minutes.'))


def validate_order_quantity(value):
    """Valida que la cantidad de un item sea válida."""
    if not 1 <= value <= 100:  # Máximo 100 unidades por item
        raise ValidationError(_('Quantity must be between 1 and 100.'))