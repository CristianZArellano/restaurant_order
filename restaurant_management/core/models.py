"""
Modelos base y mixins reutilizables.
Aplicando principios DRY y Single Responsibility.
"""

from django.db import models


class TimestampedModel(models.Model):
    """Mixin para agregar timestamps a los modelos."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
        help_text="Fecha y hora de creación del registro",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
        help_text="Fecha y hora de la última modificación",
    )

    class Meta:
        abstract = True


class ActiveModel(models.Model):
    """Mixin para modelos con estado activo/inactivo."""

    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el registro está activo",
    )

    class Meta:
        abstract = True


class SlugModel(models.Model):
    """Mixin para modelos que necesitan slug."""

    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name="Slug",
        help_text="URL amigable generada automáticamente",
    )

    class Meta:
        abstract = True
