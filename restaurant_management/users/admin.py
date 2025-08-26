from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del admin para CustomUser
    """

    # Agregar campos adicionales al formulario del admin
    fieldsets = UserAdmin.fieldsets + (
        (
            "Información adicional",
            {"fields": ("phone", "is_verified", "created_at", "updated_at")},
        ),
    )

    # Campos adicionales al crear usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información adicional",
            {
                "classes": ("wide",),
                "fields": ("email", "phone", "is_verified"),
            },
        ),
    )

    # Campos solo lectura
    readonly_fields = ("created_at", "updated_at")

    # Campos que se muestran en la lista de usuarios
    list_display = (
        "username",
        "email",
        "phone",
        "is_verified_display",
        "is_staff",
        "is_active",
        "date_joined",
        "restaurants_count",
    )

    # Filtros laterales
    list_filter = ("is_verified", "is_staff", "is_active", "created_at", "date_joined")

    # Campos de búsqueda
    search_fields = ("username", "email", "phone", "first_name", "last_name")

    # Orden por defecto
    ordering = ("-date_joined",)

    # Cantidad de usuarios por página
    list_per_page = 25

    # Barra de navegación por fecha
    date_hierarchy = "date_joined"

    def is_verified_display(self, obj):
        """Muestra el estado de verificación con iconos"""
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verificado</span>')
        return format_html('<span style="color: red;">✗ No verificado</span>')

    is_verified_display.short_description = "Verificado"

    def restaurants_count(self, obj):
        """Cuenta los restaurantes del usuario"""
        return obj.restaurants.count()

    restaurants_count.short_description = "Restaurantes"

    def get_queryset(self, request):
        """Optimiza las consultas con prefetch_related"""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("restaurants")
