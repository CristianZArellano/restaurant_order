from django.core.validators import MinValueValidator
from django.db import models


class Order(models.Model):
    # Relaciones
    restaurant = models.ForeignKey(
        "restaurants.Restaurant", on_delete=models.CASCADE, related_name="orders"
    )
    user = models.ForeignKey(
        "users.CustomUser", on_delete=models.CASCADE, related_name="orders"
    )

    # Total de la orden con validación
    total = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Estados de la orden
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PREPARING", "Preparing"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Representación en string
    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.restaurant.name} - {self.total} - {self.status}"
