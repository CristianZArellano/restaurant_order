"""
Tests completos para el modelo Restaurant.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .models import Restaurant

User = get_user_model()


class RestaurantModelTestCase(TestCase):
    """Tests para el modelo Restaurant."""

    def setUp(self):
        """Configuración inicial para tests."""
        self.user = User.objects.create_user(
            username='restaurant_owner',
            email='owner@restaurant.com',
            password='testpass123'
        )
        
        self.restaurant_data = {
            'name': 'Test Restaurant',
            'location': 'Test City, Test Street 123',
            'phone': '+573001234567',
            'description': 'A great test restaurant',
            'email': 'restaurant@test.com',
            'owner': self.user
        }

    def test_create_restaurant_valid(self):
        """Test crear restaurante válido."""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(restaurant.location, 'Test City, Test Street 123')
        self.assertEqual(restaurant.phone, '+573001234567')
        self.assertEqual(restaurant.email, 'restaurant@test.com')
        self.assertEqual(restaurant.owner, self.user)
        self.assertTrue(restaurant.is_active)
        self.assertIsNotNone(restaurant.slug)

    def test_slug_auto_generation(self):
        """Test generación automática de slug."""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        
        self.assertEqual(restaurant.slug, 'test-restaurant')

    def test_slug_uniqueness(self):
        """Test unicidad de slug con nombres duplicados."""
        # Crear primer restaurante
        Restaurant.objects.create(**self.restaurant_data)
        
        # Crear segundo restaurante con mismo nombre
        user2 = User.objects.create_user(
            username='owner2',
            password='pass123'
        )
        restaurant_data_2 = self.restaurant_data.copy()
        restaurant_data_2['owner'] = user2
        restaurant_data_2['location'] = 'Another location'
        
        restaurant2 = Restaurant.objects.create(**restaurant_data_2)
        
        self.assertEqual(restaurant2.slug, 'test-restaurant-1')

    def test_restaurant_str_representation(self):
        """Test representación string del restaurante."""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        expected = "Test Restaurant - Test City, Test Street 123"
        self.assertEqual(str(restaurant), expected)

    def test_full_address_property(self):
        """Test propiedad full_address."""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        expected = "Test Restaurant, Test City, Test Street 123"
        self.assertEqual(restaurant.full_address, expected)

    def test_invalid_phone_validation(self):
        """Test validación de teléfono inválido."""
        restaurant_data = self.restaurant_data.copy()
        restaurant_data['phone'] = 'invalid-phone'
        
        with self.assertRaises(ValidationError):
            restaurant = Restaurant(**restaurant_data)
            restaurant.full_clean()

    def test_empty_name_validation(self):
        """Test validación de nombre vacío."""
        restaurant_data = self.restaurant_data.copy()
        restaurant_data['name'] = '   '  # Solo espacios
        
        with self.assertRaises(ValidationError):
            restaurant = Restaurant(**restaurant_data)
            restaurant.full_clean()

    def test_unique_name_constraint(self):
        """Test restricción de nombre único."""
        Restaurant.objects.create(**self.restaurant_data)
        
        # Intentar crear otro restaurante con mismo nombre
        user2 = User.objects.create_user(
            username='owner2',
            password='pass123'
        )
        restaurant_data_2 = self.restaurant_data.copy()
        restaurant_data_2['owner'] = user2
        
        with self.assertRaises(IntegrityError):
            Restaurant.objects.create(**restaurant_data_2)

    def test_timestamps_auto_update(self):
        """Test que timestamps se actualicen automáticamente."""
        restaurant = Restaurant.objects.create(**self.restaurant_data)
        
        created_at = restaurant.created_at
        updated_at = restaurant.updated_at
        
        # Esperar un poco y actualizar
        import time
        time.sleep(0.1)
        
        restaurant.description = 'Updated description'
        restaurant.save()
        
        restaurant.refresh_from_db()
        
        # created_at no debe cambiar, updated_at sí
        self.assertEqual(restaurant.created_at, created_at)
        self.assertGreater(restaurant.updated_at, updated_at)
