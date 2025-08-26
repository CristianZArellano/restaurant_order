"""
Managers personalizados para optimizar consultas y encapsular lógica de negocio.
Aplicando principios SOLID y separación de responsabilidades.
"""
from decimal import Decimal
from django.db import models
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta


class ActiveManager(models.Manager):
    """Manager base para objetos con estado activo/inactivo."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class RestaurantManager(models.Manager):
    """Manager personalizado para Restaurant con consultas optimizadas."""
    
    def active(self):
        """Retorna solo restaurantes activos."""
        return self.filter(is_active=True)
    
    def by_owner(self, user):
        """Restaurantes de un propietario específico."""
        return self.filter(owner=user)
    
    def with_menu_stats(self):
        """Restaurantes con estadísticas de menú."""
        return self.select_related('owner').annotate(
            menu_items_count=Count('menu_items'),
            orders_count=Count('orders'),
            avg_rating=Avg('orders__review__rating')
        )
    
    def search(self, query):
        """Búsqueda de restaurantes por nombre o ubicación."""
        return self.filter(
            Q(name__icontains=query) | 
            Q(location__icontains=query)
        ).distinct()


class MenuItemManager(models.Manager):
    """Manager para MenuItem con consultas específicas."""
    
    def available(self):
        """Items disponibles del menú."""
        return self.filter(is_available=True)
    
    def by_category(self, category):
        """Items por categoría."""
        return self.filter(category=category, is_available=True)
    
    def by_restaurant(self, restaurant):
        """Items de un restaurante específico."""
        return self.filter(restaurant=restaurant, is_available=True)
    
    def with_restaurant_info(self):
        """Items con información del restaurante."""
        return self.select_related('restaurant')


class OrderQuerySet(models.QuerySet):
    """QuerySet personalizado para Order."""
    
    def active(self):
        """Órdenes activas (no entregadas ni canceladas)."""
        return self.exclude(status__in=['DELIVERED', 'CANCELLED'])
    
    def pending(self):
        """Órdenes pendientes."""
        return self.filter(status='PENDING')
    
    def in_progress(self):
        """Órdenes en progreso."""
        return self.filter(status__in=['CONFIRMED', 'PREPARING', 'READY', 'OUT_FOR_DELIVERY'])
    
    def completed(self):
        """Órdenes completadas."""
        return self.filter(status='DELIVERED')
    
    def cancelled(self):
        """Órdenes canceladas."""
        return self.filter(status='CANCELLED')
    
    def by_restaurant(self, restaurant):
        """Órdenes de un restaurante específico."""
        return self.filter(restaurant=restaurant)
    
    def by_user(self, user):
        """Órdenes de un usuario específico."""
        return self.filter(user=user)
    
    def today(self):
        """Órdenes de hoy."""
        today = timezone.now().date()
        return self.filter(created_at__date=today)
    
    def this_week(self):
        """Órdenes de esta semana."""
        week_start = timezone.now() - timedelta(days=7)
        return self.filter(created_at__gte=week_start)
    
    def this_month(self):
        """Órdenes de este mes."""
        month_start = timezone.now().replace(day=1)
        return self.filter(created_at__gte=month_start)
    
    def with_totals(self):
        """Órdenes con totales calculados."""
        return self.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total'),
            average_order_value=Avg('total')
        )


class OrderManager(models.Manager):
    """Manager personalizado para Order."""
    
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)
    
    def active(self):
        return self.get_queryset().active()
    
    def pending(self):
        return self.get_queryset().pending()
    
    def in_progress(self):
        return self.get_queryset().in_progress()
    
    def completed(self):
        return self.get_queryset().completed()
    
    def cancelled(self):
        return self.get_queryset().cancelled()
    
    def by_restaurant(self, restaurant):
        return self.get_queryset().by_restaurant(restaurant)
    
    def by_user(self, user):
        return self.get_queryset().by_user(user)
    
    def today(self):
        return self.get_queryset().today()
    
    def this_week(self):
        return self.get_queryset().this_week()
    
    def this_month(self):
        return self.get_queryset().this_month()
    
    def with_related(self):
        """Órdenes con relaciones optimizadas."""
        return self.select_related('user', 'restaurant').prefetch_related(
            'order_items__menu_item',
            'status_history'
        )
    
    def create_order(self, user, restaurant, order_type='DELIVERY', **kwargs):
        """Factory method para crear órdenes con valores por defecto."""
        return self.create(
            user=user,
            restaurant=restaurant,
            order_type=order_type,
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            delivery_fee=Decimal('0.00'),
            total=Decimal('0.01'),  # Mínimo requerido
            **kwargs
        )


class OrderItemManager(models.Manager):
    """Manager para OrderItem."""
    
    def by_order(self, order):
        """Items de una orden específica."""
        return self.filter(order=order).select_related('menu_item')
    
    def by_menu_item(self, menu_item):
        """Histórico de un item del menú."""
        return self.filter(menu_item=menu_item).select_related('order')


class ReviewManager(models.Manager):
    """Manager para Review."""
    
    def by_restaurant(self, restaurant):
        """Reviews de un restaurante."""
        return self.filter(order__restaurant=restaurant)
    
    def by_rating(self, rating):
        """Reviews por calificación."""
        return self.filter(rating=rating)
    
    def recent(self, days=30):
        """Reviews recientes."""
        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since)
    
    def restaurant_stats(self, restaurant):
        """Estadísticas de reviews para un restaurante."""
        reviews = self.by_restaurant(restaurant)
        return reviews.aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating'),
            rating_1=Count('id', filter=Q(rating=1)),
            rating_2=Count('id', filter=Q(rating=2)),
            rating_3=Count('id', filter=Q(rating=3)),
            rating_4=Count('id', filter=Q(rating=4)),
            rating_5=Count('id', filter=Q(rating=5)),
        )