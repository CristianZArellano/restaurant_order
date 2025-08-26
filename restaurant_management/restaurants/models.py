from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Restaurant(models.Model):
    # Nombre del restaurante (único)
    name = models.CharField(max_length=255, unique=True)

    # Ubicación/dirección
    location = models.CharField(max_length=255)

    # Teléfono con validación
    phone_regex = RegexValidator(
        regex=r"^\+?\d{7,15}$",
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
    )
    phone = models.CharField(validators=[phone_regex], max_length=16, blank=True)

    # Slug para URLs amigables
    slug = models.SlugField(unique=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Estado activo/inactivo
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Generar slug automáticamente si no existe
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            num = 1
            while Restaurant.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.location}"
