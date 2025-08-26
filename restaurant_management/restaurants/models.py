"""
Modelo de Restaurant refactorizado aplicando principios SOLID y LEAN Code.
"""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.validators import PhoneNumberValidator
from core.models import TimestampedModel, ActiveModel, SlugModel
from core.managers import RestaurantManager

User = get_user_model()


class Restaurant(TimestampedModel, ActiveModel, SlugModel):
    """
    Modelo que representa un restaurante con información básica y de contacto.
    
    Attributes:
        name (str): Nombre único del restaurante
        location (str): Ubicación/dirección del restaurante
        phone (str): Número telefónico de contacto
        description (str): Descripción opcional del restaurante
        email (str): Email de contacto
        owner (User): Propietario del restaurante
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Nombre"),
        help_text=_("Nombre único del restaurante")
    )

    location = models.CharField(
        max_length=255,
        verbose_name=_("Ubicación"),
        help_text=_("Dirección física del restaurante")
    )

    phone = models.CharField(
        validators=[PhoneNumberValidator()],
        max_length=16,
        blank=True,
        verbose_name=_("Teléfono"),
        help_text=_("Número telefónico de contacto")
    )

    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción del restaurante y su oferta gastronómica")
    )

    email = models.EmailField(
        blank=True,
        verbose_name=_("Email"),
        help_text=_("Email de contacto del restaurante")
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="restaurants",
        verbose_name=_("Propietario"),
        help_text=_("Usuario propietario del restaurante")
    )

    # Managers
    objects = RestaurantManager()

    class Meta:
        verbose_name = _("Restaurante")
        verbose_name_plural = _("Restaurantes")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["owner"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        """Representación string del restaurante."""
        return f"{self.name} - {self.location}"

    def clean(self):
        """Validación personalizada del modelo."""
        super().clean()
        
        # Validar que el nombre no esté vacío después de strip
        if not self.name.strip():
            raise ValidationError({
                'name': _("Restaurant name cannot be empty.")
            })
        
        # Validar formato del email si se proporciona
        if self.email and not self._is_valid_email_format():
            raise ValidationError({
                'email': _("Invalid email format.")
            })

    def save(self, *args, **kwargs):
        """Override save para generar slug automáticamente."""
        self._generate_slug()
        super().save(*args, **kwargs)

    def _generate_slug(self):
        """Genera slug único automáticamente si no existe."""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug

    def _is_valid_email_format(self):
        """Validación básica de formato de email."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None

    @property
    def full_address(self):
        """Devuelve la dirección completa del restaurante."""
        return f"{self.name}, {self.location}"

    @property
    def menu_items_count(self):
        """Número de items disponibles en el menú."""
        return self.menu_items.filter(is_available=True).count()

    @property
    def total_orders(self):
        """Número total de órdenes recibidas."""
        return self.orders.count()

    @property
    def active_orders_count(self):
        """Número de órdenes activas."""
        return self.orders.active().count()

    @property
    def average_rating(self):
        """Calificación promedio del restaurante."""
        from django.db.models import Avg
        result = self.orders.aggregate(
            avg_rating=Avg('review__rating')
        )
        return result['avg_rating'] or 0

    def get_recent_orders(self, days=7):
        """Obtiene órdenes recientes del restaurante."""
        return self.orders.this_week() if days == 7 else self.orders.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )
