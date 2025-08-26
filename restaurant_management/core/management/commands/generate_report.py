"""
Comando para generar reportes del sistema.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta

from restaurants.models import Restaurant
from orders.models import Order, Review, OrderStatus

User = get_user_model()


class Command(BaseCommand):
    help = 'Generar reportes del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['summary', 'restaurants', 'orders', 'users'],
            default='summary',
            help='Tipo de reporte a generar'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Período en días para el reporte (default: 30)'
        )

    def handle(self, *args, **options):
        """Ejecuta el comando."""
        report_type = options['type']
        days = options['days']
        
        self.stdout.write(f'Generando reporte: {report_type.upper()}')
        self.stdout.write(f'Período: últimos {days} días')
        self.stdout.write('=' * 50)
        
        if report_type == 'summary':
            self.generate_summary_report(days)
        elif report_type == 'restaurants':
            self.generate_restaurants_report(days)
        elif report_type == 'orders':
            self.generate_orders_report(days)
        elif report_type == 'users':
            self.generate_users_report(days)

    def generate_summary_report(self, days):
        """Genera reporte resumen."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Estadísticas generales
        total_users = User.objects.count()
        total_restaurants = Restaurant.objects.count()
        active_restaurants = Restaurant.objects.filter(is_active=True).count()
        
        # Estadísticas de órdenes
        total_orders = Order.objects.count()
        recent_orders = Order.objects.filter(created_at__gte=cutoff_date)
        
        orders_by_status = recent_orders.values('status').annotate(
            count=Count('id')
        )
        
        # Estadísticas financieras
        revenue_stats = recent_orders.aggregate(
            total_revenue=Sum('total'),
            average_order=Avg('total'),
            order_count=Count('id')
        )
        
        # Estadísticas de reviews
        review_stats = Review.objects.filter(
            created_at__gte=cutoff_date
        ).aggregate(
            total_reviews=Count('id'),
            average_rating=Avg('rating')
        )
        
        # Mostrar resultados
        self.stdout.write('\n📊 ESTADÍSTICAS GENERALES')
        self.stdout.write(f'Total usuarios: {total_users}')
        self.stdout.write(f'Total restaurantes: {total_restaurants}')
        self.stdout.write(f'Restaurantes activos: {active_restaurants}')
        
        self.stdout.write('\n📦 ESTADÍSTICAS DE ÓRDENES')
        self.stdout.write(f'Total órdenes históricas: {total_orders}')
        self.stdout.write(f'Órdenes últimos {days} días: {recent_orders.count()}')
        
        for status_data in orders_by_status:
            status_display = dict(OrderStatus.choices).get(
                status_data['status'], 
                status_data['status']
            )
            self.stdout.write(f'  - {status_display}: {status_data["count"]}')
        
        self.stdout.write('\n💰 ESTADÍSTICAS FINANCIERAS')
        if revenue_stats['total_revenue']:
            self.stdout.write(f'Ingresos período: ${revenue_stats["total_revenue"]:,.2f}')
            self.stdout.write(f'Promedio por orden: ${revenue_stats["average_order"]:,.2f}')
        else:
            self.stdout.write('Sin ingresos en el período')
        
        self.stdout.write('\n⭐ ESTADÍSTICAS DE REVIEWS')
        if review_stats['total_reviews']:
            self.stdout.write(f'Total reviews: {review_stats["total_reviews"]}')
            self.stdout.write(f'Rating promedio: {review_stats["average_rating"]:.2f}/5')
        else:
            self.stdout.write('Sin reviews en el período')

    def generate_restaurants_report(self, days):
        """Genera reporte de restaurantes."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        restaurants = Restaurant.objects.annotate(
            total_orders=Count('orders'),
            recent_orders=Count(
                'orders',
                filter=Q(orders__created_at__gte=cutoff_date)
            ),
            total_revenue=Sum('orders__total'),
            avg_rating=Avg('orders__review__rating')
        ).order_by('-recent_orders')
        
        self.stdout.write('\n🏪 TOP RESTAURANTES (por órdenes recientes)')
        self.stdout.write('-' * 80)
        
        for restaurant in restaurants[:10]:
            self.stdout.write(
                f'{restaurant.name:<30} | '
                f'Órdenes: {restaurant.recent_orders:>3} | '
                f'Total hist: {restaurant.total_orders:>3} | '
                f'Rating: {restaurant.avg_rating or 0:.1f}/5'
            )

    def generate_orders_report(self, days):
        """Genera reporte de órdenes."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        recent_orders = Order.objects.filter(
            created_at__gte=cutoff_date
        ).select_related('user', 'restaurant')
        
        self.stdout.write(f'\n📦 ÓRDENES RECIENTES (últimos {days} días)')
        self.stdout.write('-' * 100)
        
        for order in recent_orders.order_by('-created_at')[:20]:
            status_display = dict(OrderStatus.choices).get(order.status, order.status)
            self.stdout.write(
                f'{order.order_number:<15} | '
                f'{order.restaurant.name:<25} | '
                f'{order.user.username:<15} | '
                f'${order.total:>8.2f} | '
                f'{status_display:<12} | '
                f'{order.created_at.strftime("%Y-%m-%d %H:%M")}'
            )

    def generate_users_report(self, days):
        """Genera reporte de usuarios."""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        users = User.objects.annotate(
            total_orders=Count('orders'),
            recent_orders=Count(
                'orders',
                filter=Q(orders__created_at__gte=cutoff_date)
            ),
            total_spent=Sum('orders__total')
        ).order_by('-recent_orders')
        
        self.stdout.write('\n👥 TOP USUARIOS (por actividad reciente)')
        self.stdout.write('-' * 80)
        
        for user in users[:15]:
            self.stdout.write(
                f'{user.username:<20} | '
                f'Órdenes recientes: {user.recent_orders:>3} | '
                f'Total hist: {user.total_orders:>3} | '
                f'Gastado: ${user.total_spent or 0:>8.2f}'
            )