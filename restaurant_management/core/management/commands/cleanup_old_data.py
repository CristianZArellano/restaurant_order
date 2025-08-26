"""
Comando para limpiar datos antiguos del sistema.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from orders.models import Order, OrderStatusHistory, OrderStatus


class Command(BaseCommand):
    help = 'Limpiar datos antiguos del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Días de antigüedad para considerar datos como antiguos (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se eliminaría sin eliminar realmente'
        )

    def handle(self, *args, **options):
        """Ejecuta el comando."""
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            f'Limpiando datos más antiguos que {cutoff_date.strftime("%Y-%m-%d")}'
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('MODO DRY-RUN - No se eliminarán datos'))
        
        with transaction.atomic():
            # Órdenes canceladas antiguas
            cancelled_orders = Order.objects.filter(
                status=OrderStatus.CANCELLED,
                created_at__lt=cutoff_date
            )
            
            self.stdout.write(
                f'Órdenes canceladas a eliminar: {cancelled_orders.count()}'
            )
            
            if not dry_run:
                cancelled_orders.delete()
            
            # Historial de estados muy antiguos (más de 1 año)
            old_cutoff = timezone.now() - timedelta(days=365)
            old_history = OrderStatusHistory.objects.filter(
                created_at__lt=old_cutoff
            )
            
            self.stdout.write(
                f'Registros de historial antiguos a eliminar: {old_history.count()}'
            )
            
            if not dry_run:
                old_history.delete()
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('Limpieza completada exitosamente')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Vista previa de limpieza completada')
            )