from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import Restaurant

# Obtener el modelo de usuario personalizado
User = get_user_model()


# El CustomUserAdmin debe estar en users/admin.py, no aquí


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Restaurant
    """

    # Campos que se muestran en la lista
    list_display = (
        "name",
        "location",
        "owner",
        "phone",
        "is_active_display",
        "is_active",
        "created_at",
    )

    # Campos por los que se puede filtrar
    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
        "owner",
    )

    # Campos de búsqueda
    search_fields = (
        "name",
        "location",
        "phone",
        "email",
        "owner__username",
        "owner__email",
    )

    # Campos solo lectura
    readonly_fields = (
        "slug",
        "created_at",
        "updated_at",
    )

    # Campos del formulario organizados
    fieldsets = (
        ("Información básica", {"fields": ("name", "slug", "description")}),
        ("Contacto", {"fields": ("location", "phone", "email")}),
        ("Configuración", {"fields": ("owner", "is_active")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    # Campos editables desde la lista
    list_editable = ("is_active",)

    # Orden por defecto
    ordering = ("name",)

    # Cantidad por página
    list_per_page = 20

    # Barra de navegación por fecha
    date_hierarchy = "created_at"

    # Campos prepopulados (slug se genera automáticamente)
    prepopulated_fields = {}

    def is_active_display(self, obj):
        """Muestra el estado activo con iconos"""
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Activo</span>')
        return format_html('<span style="color: red;">✗ Inactivo</span>')

    is_active_display.short_description = "Estado"

    def get_queryset(self, request):
        """Optimiza las consultas con select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related("owner")

    def save_model(self, request, obj, form, change):
        """Asigna el usuario actual como propietario si es nuevo y no se especifica"""
        if not change and not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
