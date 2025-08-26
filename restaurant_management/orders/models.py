"""
Modelos del sistema de órdenes refactorizados aplicando principios SOLID y LEAN Code.
Optimizados para rendimiento y mantenibilidad.
"""
import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.validators import (
    validate_positive_decimal, 
    validate_rating, 
    validate_preparation_time,
    validate_order_quantity,
    PhoneNumberValidator
)
from core.models import TimestampedModel, ActiveModel
from core.managers import MenuItemManager, OrderManager, OrderItemManager, ReviewManager

User = get_user_model()


class MenuItemCategory(models.TextChoices):
    """Choices para categorías de menú."""
    APPETIZER = "APPETIZER", _("Entrada")
    MAIN = "MAIN", _("Plato Principal")  
    DESSERT = "DESSERT", _("Postre")
    DRINK = "DRINK", _("Bebida")
    SIDE = "SIDE", _("Acompañamiento")


class OrderStatus(models.TextChoices):
    """Choices para estados de orden."""
    PENDING = "PENDING", _("Pendiente")
    CONFIRMED = "CONFIRMED", _("Confirmada")
    PREPARING = "PREPARING", _("En preparación")
    READY = "READY", _("Lista")
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY", _("En camino")
    DELIVERED = "DELIVERED", _("Entregada")
    CANCELLED = "CANCELLED", _("Cancelada")


class OrderType(models.TextChoices):
    """Choices para tipos de orden."""
    DELIVERY = "DELIVERY", _("Domicilio")
    PICKUP = "PICKUP", _("Recoger en tienda")
    DINE_IN = "DINE_IN", _("Comer en restaurante")


class MenuItem(TimestampedModel, ActiveModel):
    """
    Modelo para elementos del menú de un restaurante.
    
    Attributes:
        restaurant: Restaurante al que pertenece el item
        name: Nombre del item del menú
        description: Descripción detallada
        price: Precio del item
        category: Categoría del item
        preparation_time: Tiempo de preparación en minutos
    """
    
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="menu_items",
        verbose_name=_("Restaurante")
    )
    
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nombre"),
        help_text=_("Nombre del elemento del menú")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Descripción"),
        help_text=_("Descripción detallada del plato")
    )
    
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[validate_positive_decimal],
        verbose_name=_("Precio"),
        help_text=_("Precio en la moneda local")
    )
    
    category = models.CharField(
        max_length=20,
        choices=MenuItemCategory.choices,
        verbose_name=_("Categoría"),
        help_text=_("Categoría del elemento del menú")
    )
    
    preparation_time = models.PositiveIntegerField(
        default=15,
        validators=[validate_preparation_time],
        verbose_name=_("Tiempo de preparación"),
        help_text=_("Tiempo de preparación en minutos")
    )
    
    # Managers
    objects = MenuItemManager()

    class Meta:
        verbose_name = _("Elemento del Menú")
        verbose_name_plural = _("Elementos del Menú")
        ordering = ["category", "name"]
        indexes = [
            models.Index(fields=["restaurant", "category"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["price"]),
        ]
        unique_together = ["restaurant", "name"]

    def __str__(self):
        return f"{self.name} - ${self.price} ({self.restaurant.name})"

    def clean(self):
        """Validación personalizada."""
        super().clean()
        
        if not self.name.strip():
            raise ValidationError({
                'name': _("Item name cannot be empty.")
            })

    @property
    def is_available(self):
        """Alias para is_active para mantener compatibilidad."""
        return self.is_active


class Order(TimestampedModel):
    """
    Modelo principal para órdenes de restaurante.
    Optimizado con managers personalizados y cálculo automático de totales.
    """
    
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Restaurante")
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name=_("Cliente")
    )
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name=_("Número de orden"),
        help_text=_("Número único de orden generado automáticamente")
    )
    
    # Totales financieros
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
        verbose_name=_("Subtotal")
    )
    
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
        verbose_name=_("Impuestos")
    )
    
    delivery_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[validate_positive_decimal],
        verbose_name=_("Costo de envío")
    )
    
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validate_positive_decimal],
        verbose_name=_("Total")
    )
    
    # Estado y tipo
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name=_("Estado")
    )
    
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.DELIVERY,
        verbose_name=_("Tipo de orden")
    )
    
    # Información de entrega
    delivery_address = models.TextField(
        blank=True,
        verbose_name=_("Dirección de entrega"),
        help_text=_("Dirección completa para entrega")
    )
    
    delivery_notes = models.TextField(
        blank=True,
        verbose_name=_("Notas especiales"),
        help_text=_("Instrucciones especiales para la entrega")
    )
    
    phone_number = models.CharField(
        validators=[PhoneNumberValidator()],
        max_length=16,
        blank=True,
        verbose_name=_("Teléfono de contacto")
    )
    
    # Tiempos de entrega
    estimated_delivery_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Tiempo estimado de entrega")
    )
    
    actual_delivery_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Hora real de entrega")
    )
    
    # Managers
    objects = OrderManager()

    class Meta:
        verbose_name = _("Orden")
        verbose_name_plural = _("Órdenes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["restaurant", "status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["order_type"]),
        ]

    def __str__(self):
        return f"Orden {self.order_number} - {self.user.username} - {self.restaurant.name}"

    def clean(self):
        """Validación personalizada."""
        super().clean()
        
        # Validar dirección para delivery
        if self.order_type == OrderType.DELIVERY and not self.delivery_address.strip():
            raise ValidationError({
                'delivery_address': _("Delivery address is required for delivery orders.")
            })

    def save(self, *args, **kwargs):
        """Override save para lógica automática."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        
        self._calculate_total()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Genera número único de orden."""
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    def _calculate_total(self):
        """Calcula el total automáticamente."""
        if not self.subtotal:
            self.subtotal = Decimal("0.00")
        if not self.tax_amount:
            self.tax_amount = Decimal("0.00") 
        if not self.delivery_fee:
            self.delivery_fee = Decimal("0.00")
            
        self.total = self.subtotal + self.tax_amount + self.delivery_fee
        
        # Asegurar mínimo de 0.01
        if self.total < Decimal("0.01"):
            self.total = Decimal("0.01")

    @property
    def is_active(self):
        """Determina si la orden está activa."""
        return self.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]

    @property
    def can_be_cancelled(self):
        """Determina si la orden puede ser cancelada."""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]

    @transaction.atomic
    def calculate_totals(self):
        """Recalcula totales basado en los items."""
        from django.db.models import Sum, F
        
        # Calcular subtotal desde items
        items_total = self.order_items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total'] or Decimal('0.00')
        
        self.subtotal = items_total
        self.tax_amount = self.subtotal * Decimal("0.08")  # 8% tax
        
        # El delivery_fee se mantiene como está configurado
        self.total = self.subtotal + self.tax_amount + self.delivery_fee
        
        return {
            "subtotal": self.subtotal,
            "tax_amount": self.tax_amount,
            "delivery_fee": self.delivery_fee,
            "total": self.total,
        }

    def update_status(self, new_status, changed_by=None, notes=""):
        """Actualiza estado de la orden y crea historial."""
        old_status = self.status
        self.status = new_status
        
        # Actualizar tiempos automáticamente
        if new_status == OrderStatus.CONFIRMED and not self.estimated_delivery_time:
            from datetime import timedelta
            self.estimated_delivery_time = timezone.now() + timedelta(minutes=45)
        elif new_status == OrderStatus.DELIVERED and not self.actual_delivery_time:
            self.actual_delivery_time = timezone.now()
        
        self.save()
        
        # Crear historial
        OrderStatusHistory.objects.create(
            order=self,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            notes=notes
        )


class OrderItem(models.Model):
    """
    Items individuales dentro de una orden.
    Optimizado para evitar duplicados y cálculos automáticos.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name=_("Orden")
    )
    
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE,
        verbose_name=_("Elemento del menú")
    )
    
    quantity = models.PositiveIntegerField(
        validators=[validate_order_quantity],
        verbose_name=_("Cantidad")
    )
    
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[validate_positive_decimal],
        verbose_name=_("Precio unitario")
    )
    
    special_instructions = models.TextField(
        blank=True,
        verbose_name=_("Instrucciones especiales")
    )
    
    # Managers
    objects = OrderItemManager()

    class Meta:
        verbose_name = _("Item de Orden")
        verbose_name_plural = _("Items de Orden")
        unique_together = ["order", "menu_item"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["menu_item"]),
        ]

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity} (Orden: {self.order.order_number})"

    def clean(self):
        """Validación personalizada."""
        super().clean()
        
        if self.quantity <= 0:
            raise ValidationError({
                'quantity': _("Quantity must be greater than 0.")
            })

    def save(self, *args, **kwargs):
        """Override save para guardar precio actual."""
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        """Calcula el subtotal del item."""
        return self.quantity * self.unit_price


class OrderStatusHistory(TimestampedModel):
    """
    Historial de cambios de estado de las órdenes.
    Simplificado y optimizado para consultas.
    """
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name=_("Orden")
    )
    
    previous_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        verbose_name=_("Estado anterior")
    )
    
    new_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        verbose_name=_("Nuevo estado")
    )
    
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Cambiado por")
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notas")
    )

    class Meta:
        verbose_name = _("Historial de Estado")
        verbose_name_plural = _("Historiales de Estado")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "-created_at"]),
            models.Index(fields=["new_status"]),
        ]

    def __str__(self):
        return f"Orden {self.order.order_number}: {self.previous_status} → {self.new_status}"


class Review(TimestampedModel):
    """
    Reviews/calificaciones de órdenes.
    Optimizado con validaciones robustas.
    """
    
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name=_("Orden")
    )
    
    rating = models.IntegerField(
        validators=[validate_rating],
        verbose_name=_("Calificación"),
        help_text=_("Calificación de 1 a 5 estrellas")
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name=_("Comentario"),
        help_text=_("Comentario opcional sobre la orden")
    )
    
    # Managers
    objects = ReviewManager()

    class Meta:
        verbose_name = _("Reseña")
        verbose_name_plural = _("Reseñas")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rating"]),
            models.Index(fields=["order"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Review de {self.order.user.username} - {self.rating}⭐"

    def clean(self):
        """Validación personalizada."""
        super().clean()
        
        # Solo permitir review si la orden está entregada
        if self.order.status != OrderStatus.DELIVERED:
            raise ValidationError({
                '__all__': _("Reviews can only be created for delivered orders.")
            })