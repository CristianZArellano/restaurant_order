from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    # Teléfono internacional (opcional)
    phone_regex = RegexValidator(
        regex=r"^\+?\d{7,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=16, blank=True)

    # Estado de verificación de la cuenta
    is_verified = models.BooleanField(default=False)

    # Timestamps adicionales (opcional)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Retorna username y email si existe
        return f"{self.username} ({self.email})" if self.email else self.username
