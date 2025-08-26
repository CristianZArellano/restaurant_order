"""
Tests para validators y utilidades del core.
"""
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError

from .validators import (
    PhoneNumberValidator,
    validate_positive_decimal,
    validate_rating,
    validate_preparation_time,
    validate_order_quantity
)


class ValidatorsTestCase(TestCase):
    """Tests para validadores personalizados."""

    def test_phone_number_validator_valid(self):
        """Test válido para validador de teléfono."""
        validator = PhoneNumberValidator()
        
        # Números válidos
        valid_phones = [
            '+1234567890',
            '1234567890',
            '+571234567890',
            '3001234567'
        ]
        
        for phone in valid_phones:
            try:
                validator(phone)
            except ValidationError:
                self.fail(f"Phone {phone} should be valid")

    def test_phone_number_validator_invalid(self):
        """Test inválido para validador de teléfono."""
        validator = PhoneNumberValidator()
        
        # Números inválidos
        invalid_phones = [
            '123',  # Muy corto
            '+' * 20,  # Muy largo
            'abc123',  # Letras
            '+1-234-567-890',  # Guiones
            ''  # Vacío
        ]
        
        for phone in invalid_phones:
            with self.assertRaises(ValidationError):
                validator(phone)

    def test_validate_positive_decimal(self):
        """Test para validador de decimales positivos."""
        # Válidos
        validate_positive_decimal(Decimal('0.01'))
        validate_positive_decimal(Decimal('100.50'))
        
        # Inválidos
        with self.assertRaises(ValidationError):
            validate_positive_decimal(Decimal('0'))
        
        with self.assertRaises(ValidationError):
            validate_positive_decimal(Decimal('-10.50'))

    def test_validate_rating(self):
        """Test para validador de rating."""
        # Válidos
        for rating in [1, 2, 3, 4, 5]:
            validate_rating(rating)
        
        # Inválidos
        for rating in [0, 6, -1, 10]:
            with self.assertRaises(ValidationError):
                validate_rating(rating)

    def test_validate_preparation_time(self):
        """Test para validador de tiempo de preparación."""
        # Válidos
        validate_preparation_time(1)
        validate_preparation_time(30)
        validate_preparation_time(300)
        
        # Inválidos
        with self.assertRaises(ValidationError):
            validate_preparation_time(0)
        
        with self.assertRaises(ValidationError):
            validate_preparation_time(301)

    def test_validate_order_quantity(self):
        """Test para validador de cantidad de orden."""
        # Válidos
        validate_order_quantity(1)
        validate_order_quantity(50)
        validate_order_quantity(100)
        
        # Inválidos
        with self.assertRaises(ValidationError):
            validate_order_quantity(0)
        
        with self.assertRaises(ValidationError):
            validate_order_quantity(101)