from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Restaurant

# Obtener el modelo de usuario personalizado
User = get_user_model()


@receiver(post_save, sender=Restaurant)
def restaurant_created_or_updated(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea o actualiza un restaurante
    """
    if created:
        # Lógica cuando se crea un nuevo restaurante
        print(f"Nuevo restaurante creado: {instance.name}")

        # Enviar email de bienvenida (opcional)
        if instance.owner.email:
            send_mail(
                subject="¡Bienvenido a nuestra plataforma!",
                message=f'Hola {instance.owner.username}, tu restaurante "{instance.name}" ha sido registrado exitosamente.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.owner.email],
                fail_silently=True,
            )
    else:
        # Lógica cuando se actualiza un restaurante existente
        print(f"Restaurante actualizado: {instance.name}")


@receiver(pre_delete, sender=Restaurant)
def restaurant_pre_delete(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de eliminar un restaurante
    """
    print(f"Se está eliminando el restaurante: {instance.name}")

    # Aquí podrías agregar lógica para:
    # - Crear un backup de los datos
    # - Notificar al propietario
    # - Limpiar archivos relacionados, etc.


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea un nuevo usuario
    """
    if created:
        print(f"Nuevo usuario creado: {instance.username}")

        # Enviar email de bienvenida
        if instance.email:
            send_mail(
                subject="¡Bienvenido!",
                message=f"Hola {instance.username}, tu cuenta ha sido creada exitosamente.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
