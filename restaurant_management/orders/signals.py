from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Order, OrderItem, OrderStatusHistory


@receiver(pre_save, sender=Order)
def order_status_change_handler(sender, instance, **kwargs):
    """
    Signal que maneja cambios de estado de órdenes
    """
    if instance.pk:  # Solo si la orden ya existe
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Crear historial de cambio de estado
                OrderStatusHistory.objects.create(
                    order=instance,
                    previous_status=old_instance.status,
                    new_status=instance.status,
                    notes="Estado cambiado automáticamente",
                )

                # Actualizar tiempos estimados basado en el nuevo estado
                if (
                    instance.status == "CONFIRMED"
                    and not instance.estimated_delivery_time
                ):
                    # Estimar tiempo de entrega (ejemplo: 45 minutos)
                    instance.estimated_delivery_time = timezone.now() + timedelta(
                        minutes=45
                    )

                elif (
                    instance.status == "DELIVERED" and not instance.actual_delivery_time
                ):
                    instance.actual_delivery_time = timezone.now()

        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Order)
def order_created_handler(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea o actualiza una orden
    """
    if created:
        print(f"Nueva orden creada: {instance.order_number}")

        # Crear historial inicial
        OrderStatusHistory.objects.create(
            order=instance,
            previous_status="",
            new_status=instance.status,
            notes="Orden creada",
        )

        # Enviar email al usuario
        if instance.user.email:
            send_mail(
                subject=f"Orden confirmada - {instance.order_number}",
                message=f"Hola {instance.user.username},\n\n"
                f"Tu orden #{instance.order_number} ha sido confirmada.\n"
                f"Total: ${instance.total}\n"
                f"Restaurante: {instance.restaurant.name}\n\n"
                f"¡Gracias por tu pedido!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )

        # Notificar al restaurante (opcional)
        if instance.restaurant.email:
            send_mail(
                subject=f"Nueva orden recibida - {instance.order_number}",
                message=f"Nueva orden de {instance.user.username}\n"
                f"Total: ${instance.total}\n"
                f"Tipo: {instance.get_order_type_display()}\n"
                f"Estado: {instance.get_status_display()}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.restaurant.email],
                fail_silently=True,
            )

    else:
        # Orden actualizada
        print(f"Orden actualizada: {instance.order_number} - Estado: {instance.status}")

        # Enviar notificación de cambio de estado importante
        if (
            instance.status in ["READY", "OUT_FOR_DELIVERY", "DELIVERED"]
            and instance.user.email
        ):
            status_messages = {
                "READY": "Tu orden está lista para recoger",
                "OUT_FOR_DELIVERY": "Tu orden está en camino",
                "DELIVERED": "Tu orden ha sido entregada",
            }

            send_mail(
                subject=f"Actualización de orden - {instance.order_number}",
                message=f"Hola {instance.user.username},\n\n"
                f"{status_messages.get(instance.status)}\n"
                f"Orden: #{instance.order_number}\n\n"
                f"¡Gracias por elegir {instance.restaurant.name}!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=True,
            )


@receiver(post_save, sender=OrderItem)
def order_item_saved_handler(sender, instance, **kwargs):
    """
    Signal que recalcula totales cuando se modifica un item
    """
    # Recalcular totales de la orden
    order = instance.order
    totals = order.calculate_totals()

    # Actualizar la orden sin disparar signals adicionales
    Order.objects.filter(pk=order.pk).update(
        subtotal=totals["subtotal"],
        tax_amount=totals["tax_amount"],
        total=totals["total"],
    )

    print(f"Totales recalculados para orden {order.order_number}: ${totals['total']}")


@receiver(post_delete, sender=OrderItem)
def order_item_deleted_handler(sender, instance, **kwargs):
    """
    Signal que recalcula totales cuando se elimina un item
    """
    try:
        order = instance.order
        totals = order.calculate_totals()

        # Actualizar la orden
        Order.objects.filter(pk=order.pk).update(
            subtotal=totals["subtotal"],
            tax_amount=totals["tax_amount"],
            total=totals["total"],
        )

        print(
            f"Item eliminado. Totales recalculados para orden {order.order_number}: ${totals['total']}"
        )

        # Si no quedan items, cancelar la orden
        if not order.order_items.exists():
            order.status = "CANCELLED"
            order.save()
            print(f"Orden {order.order_number} cancelada - no quedan items")

    except Order.DoesNotExist:
        # La orden ya fue eliminada
        pass


@receiver(post_save, sender=OrderStatusHistory)
def status_history_created_handler(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea un registro de historial
    """
    if created:
        print(
            f"Historial creado para orden {instance.order.order_number}: "
            f"{instance.previous_status} → {instance.new_status}"
        )

        # Aquí podrías agregar lógica adicional como:
        # - Logging más detallado
        # - Notificaciones push
        # - Webhooks para sistemas externos
        # - Analytics/métricas
