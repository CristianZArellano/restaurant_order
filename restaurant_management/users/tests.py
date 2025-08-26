"""
Tests completos para el modelo CustomUser.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserModelTestCase(TestCase):
    """Tests para el modelo CustomUser."""

    def setUp(self):
        """Configuración inicial para tests."""
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "phone": "+573001234567",
            "first_name": "Test",
            "last_name": "User",
        }

    def test_create_user_valid(self):
        """Test crear usuario válido."""
        user = User.objects.create_user(**self.user_data)

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.phone, "+573001234567")
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password("testpassword123"))

    def test_create_user_without_email(self):
        """Test crear usuario sin email."""
        user_data = self.user_data.copy()
        del user_data["email"]

        user = User.objects.create_user(**user_data)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "")

    def test_create_superuser(self):
        """Test crear superusuario."""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_user_str_representation(self):
        """Test representación string del usuario."""
        # Con nombre completo
        user = User.objects.create_user(**self.user_data)
        expected = "Test User (test@example.com)"
        self.assertEqual(str(user), expected)

        # Sin nombre completo
        user_no_name = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="pass123"
        )
        expected = "testuser2 (test2@example.com)"
        self.assertEqual(str(user_no_name), expected)

        # Sin email
        user_no_email = User.objects.create_user(
            username="testuser3", password="pass123"
        )
        expected = "testuser3"
        self.assertEqual(str(user_no_email), expected)

    def test_invalid_phone_number(self):
        """Test validación de número telefónico."""
        user_data = self.user_data.copy()
        user_data["phone"] = "invalid-phone"

        with self.assertRaises(ValidationError):
            user = User(**user_data)
            user.full_clean()

    def test_duplicate_email_validation(self):
        """Test validación de email duplicado."""
        # Crear primer usuario
        User.objects.create_user(**self.user_data)

        # Intentar crear segundo usuario con mismo email
        user_data_2 = self.user_data.copy()
        user_data_2["username"] = "testuser2"

        user2 = User(**user_data_2)
        with self.assertRaises(ValidationError):
            user2.full_clean()

    def test_get_display_name(self):
        """Test método get_display_name."""
        user = User.objects.create_user(**self.user_data)

        # Con nombre completo
        self.assertEqual(user.get_display_name(), "Test User")

        # Sin nombre completo
        user.first_name = ""
        user.last_name = ""
        user.save()
        self.assertEqual(user.get_display_name(), "testuser")

    def test_restaurants_count_property(self):
        """Test propiedad restaurants_count."""
        user = User.objects.create_user(**self.user_data)

        # Sin restaurantes
        self.assertEqual(user.restaurants_count, 0)

    def test_orders_count_property(self):
        """Test propiedad orders_count."""
        user = User.objects.create_user(**self.user_data)

        # Sin órdenes
        self.assertEqual(user.orders_count, 0)

    def test_has_restaurants_property(self):
        """Test propiedad has_restaurants."""
        user = User.objects.create_user(**self.user_data)

        # Sin restaurantes
        self.assertFalse(user.has_restaurants)

    def test_user_verification_toggle(self):
        """Test cambio de estado de verificación."""
        user = User.objects.create_user(**self.user_data)

        # Inicialmente no verificado
        self.assertFalse(user.is_verified)

        # Verificar usuario
        user.is_verified = True
        user.save()

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

    def test_timestamps_auto_update(self):
        """Test que timestamps se actualicen automáticamente."""
        user = User.objects.create_user(**self.user_data)

        created_at = user.created_at
        updated_at = user.updated_at

        # Esperar un poco y actualizar
        import time

        time.sleep(0.1)

        user.phone = "+573009876543"
        user.save()

        user.refresh_from_db()

        # created_at no debe cambiar, updated_at sí
        self.assertEqual(user.created_at, created_at)
        self.assertGreater(user.updated_at, updated_at)

    def test_phone_validation_edge_cases(self):
        """Test casos edge para validación de teléfono."""
        user = User.objects.create_user(username="phonetest", password="pass123")

        # Teléfono vacío debe ser válido
        user.phone = ""
        user.full_clean()  # No debe lanzar excepción

        # Teléfonos válidos
        valid_phones = [
            "+573001234567",
            "3001234567",
            "+1234567890",
        ]

        for phone in valid_phones:
            user.phone = phone
            user.full_clean()  # No debe lanzar excepción

        # Teléfonos inválidos
        invalid_phones = [
            "123",  # Muy corto
            "+" + "1" * 20,  # Muy largo
            "abc123",  # Con letras
        ]

        for phone in invalid_phones:
            user.phone = phone
            with self.assertRaises(ValidationError):
                user.full_clean()


class CustomUserManagerTestCase(TestCase):
    """Tests para funcionalidades del manager de User."""

    def test_create_user_required_fields(self):
        """Test campos requeridos para crear usuario."""
        # Username es requerido
        with self.assertRaises(ValueError):
            User.objects.create_user(username="")

    def test_create_superuser_required_flags(self):
        """Test flags requeridos para superusuario."""
        # is_staff debe ser True
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="admin", password="pass123", is_staff=False
            )

        # is_superuser debe ser True
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="admin", password="pass123", is_superuser=False
            )
