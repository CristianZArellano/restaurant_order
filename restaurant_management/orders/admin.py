from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import MenuItem, Order, OrderItem, OrderStatusHistory, Review


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """
    Admin para elementos del menú
    """

    list_display = (
        "name",
        "restaurant",
        "category",
        "price_display",
        "is_active_display",
        "is_active",
        "preparation_time",
    )

    list_filter = (
        "category",
        "is_active",
        "restaurant",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "restaurant__name",
    )

    list_editable = ("is_active",)

    fieldsets = (
        ("Información básica", {"fields": ("name", "description", "restaurant")}),
        (
            "Detalles del producto",
            {"fields": ("category", "price", "preparation_time")},
        ),
        ("Estado", {"fields": ("is_active",)}),
    )

    def price_display(self, obj):
        return f"${obj.price}"

    price_display.short_description = "Precio"

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Disponible</span>')
        return format_html('<span style="color: red;">✗ No disponible</span>')

    is_active_display.short_description = "Estado"


class OrderItemInline(admin.TabularInline):
    """
    Inline para mostrar items de orden
    """

    model = OrderItem
    extra = 0
    fields = (
        "menu_item",
        "quantity",
        "unit_price",
        "subtotal_display",
        "special_instructions",
    )
    readonly_fields = ("subtotal_display",)

    def subtotal_display(self, obj):
        if obj.pk:
            return f"${obj.subtotal}"
        return "-"

    subtotal_display.short_description = "Subtotal"


class OrderStatusHistoryInline(admin.TabularInline):
    """
    Inline para historial de estados
    """

    model = OrderStatusHistory
    extra = 0
    fields = ("previous_status", "new_status", "changed_by", "created_at", "notes")
    readonly_fields = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin principal para órdenes
    """

    list_display = (
        "order_number",
        "user",
        "restaurant",
        "status_display",
        "status",
        "order_type",
        "total_display",
        "created_at",
        "estimated_delivery_time",
    )

    list_filter = (
        "status",
        "order_type",
        "restaurant",
        "created_at",
        "estimated_delivery_time",
    )

    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "restaurant__name",
        "phone_number",
    )

    list_editable = ("status",)

    readonly_fields = (
        "order_number",
        "total",
        "created_at",
        "updated_at",
        "items_count",
        "order_summary",
    )

    fieldsets = (
        (
            "Información de la orden",
            {"fields": ("order_number", "user", "restaurant", "status", "order_type")},
        ),
        (
            "Detalles financieros",
            {"fields": ("subtotal", "tax_amount", "delivery_fee", "total")},
        ),
        (
            "Información de entrega",
            {"fields": ("delivery_address", "phone_number", "delivery_notes")},
        ),
        ("Tiempos", {"fields": ("estimated_delivery_time", "actual_delivery_time")}),
        (
            "Resumen",
            {"fields": ("items_count", "order_summary"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    inlines = [OrderItemInline, OrderStatusHistoryInline]

    actions = ["mark_as_confirmed", "mark_as_preparing", "mark_as_ready"]

    def status_display(self, obj):
        status_colors = {
            "PENDING": "#ffc107",
            "CONFIRMED": "#17a2b8",
            "PREPARING": "#fd7e14",
            "READY": "#28a745",
            "OUT_FOR_DELIVERY": "#6f42c1",
            "DELIVERED": "#20c997",
            "CANCELLED": "#dc3545",
        }
        color = status_colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Estado"

    def total_display(self, obj):
        return f"${obj.total}"

    total_display.short_description = "Total"
    total_display.admin_order_field = "total"

    def items_count(self, obj):
        return obj.order_items.count()

    items_count.short_description = "Número de items"

    def order_summary(self, obj):
        items = obj.order_items.all()
        summary = "<ul>"
        for item in items:
            summary += (
                f"<li>{item.menu_item.name} x{item.quantity} (${item.subtotal})</li>"
            )
        summary += "</ul>"
        return mark_safe(summary)

    order_summary.short_description = "Items de la orden"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related("user", "restaurant").prefetch_related(
            "order_items__menu_item"
        )

    # Actions personalizadas
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status="PENDING").update(status="CONFIRMED")
        self.message_user(request, f"{updated} órdenes marcadas como confirmadas.")

    mark_as_confirmed.short_description = "Marcar como confirmadas"

    def mark_as_preparing(self, request, queryset):
        updated = queryset.filter(status="CONFIRMED").update(status="PREPARING")
        self.message_user(request, f"{updated} órdenes marcadas como en preparación.")

    mark_as_preparing.short_description = "Marcar como en preparación"

    def mark_as_ready(self, request, queryset):
        updated = queryset.filter(status="PREPARING").update(status="READY")
        self.message_user(request, f"{updated} órdenes marcadas como listas.")

    mark_as_ready.short_description = "Marcar como listas"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin para items individuales
    """

    list_display = (
        "order",
        "menu_item",
        "quantity",
        "unit_price",
        "subtotal_display",
    )

    list_filter = (
        "menu_item__category",
        "order__status",
        "order__restaurant",
    )

    search_fields = (
        "order__order_number",
        "menu_item__name",
        "order__user__username",
    )

    readonly_fields = ("subtotal_display",)

    def subtotal_display(self, obj):
        return f"${obj.subtotal}"

    subtotal_display.short_description = "Subtotal"


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin para historial de estados
    """

    list_display = (
        "order",
        "previous_status",
        "new_status",
        "changed_by",
        "created_at",
    )

    list_filter = (
        "previous_status",
        "new_status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "changed_by__username",
    )

    readonly_fields = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin para reviews
    """

    list_display = (
        "order",
        "rating_display",
        "created_at",
        "comment_preview",
    )

    list_filter = (
        "rating",
        "created_at",
        "order__restaurant",
    )

    search_fields = (
        "order__order_number",
        "order__user__username",
        "comment",
    )

    readonly_fields = ("created_at",)

    def rating_display(self, obj):
        stars = "⭐" * obj.rating
        return f"{stars} ({obj.rating}/5)"

    rating_display.short_description = "Calificación"

    def comment_preview(self, obj):
        if obj.comment:
            return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
        return "Sin comentario"

    comment_preview.short_description = "Comentario"
