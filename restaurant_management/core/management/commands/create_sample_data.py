"""
Comando para crear datos de prueba en el sistema.
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from restaurants.models import Restaurant
from orders.models import MenuItem, Order, OrderItem, Review, MenuItemCategory, OrderStatus

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear datos de prueba para el sistema de restaurantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Número de usuarios a crear'
        )
        parser.add_argument(
            '--restaurants',
            type=int,
            default=5,
            help='Número de restaurantes a crear'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=20,
            help='Número de órdenes a crear'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar datos existentes antes de crear nuevos'
        )

    def handle(self, *args, **options):
        """Ejecuta el comando."""
        if options['clear']:
            self.clear_data()

        with transaction.atomic():
            users = self.create_users(options['users'])
            restaurants = self.create_restaurants(options['restaurants'], users)
            self.create_menu_items(restaurants)
            orders = self.create_orders(options['orders'], users, restaurants)
            self.create_reviews(orders)

        self.stdout.write(
            self.style.SUCCESS(
                f'Datos de prueba creados exitosamente:\n'
                f'- {len(users)} usuarios\n'
                f'- {len(restaurants)} restaurantes\n'
                f'- {len(orders)} órdenes'
            )
        )

    def clear_data(self):
        """Limpia datos existentes."""
        self.stdout.write('Limpiando datos existentes...')
        
        Review.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        MenuItem.objects.all().delete()
        Restaurant.objects.all().delete()
        
        # No borrar superusers
        User.objects.filter(is_superuser=False).delete()

    def create_users(self, count):
        """Crea usuarios de prueba."""
        self.stdout.write(f'Creando {count} usuarios...')
        users = []
        
        for i in range(count):
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='testpass123',
                first_name=f'Usuario',
                last_name=f'{i+1}',
                phone=f'+57300123456{i%10}',
                is_verified=True
            )
            users.append(user)
        
        return users

    def create_restaurants(self, count, users):
        """Crea restaurantes de prueba."""
        self.stdout.write(f'Creando {count} restaurantes...')
        restaurants = []
        
        restaurant_names = [
            'Pizza Italiana', 'Burger House', 'Sushi Zen', 'Taco Loco',
            'Pasta & More', 'BBQ Central', 'Healthy Bowls', 'Coffee Corner',
            'Mexican Grill', 'Asian Fusion'
        ]
        
        locations = [
            'Bogotá, Zona Rosa', 'Medellín, El Poblado', 'Cali, San Fernando',
            'Barranquilla, Alto Prado', 'Cartagena, Centro Histórico'
        ]
        
        for i in range(count):
            restaurant = Restaurant.objects.create(
                name=restaurant_names[i % len(restaurant_names)],
                location=locations[i % len(locations)],
                phone=f'+57301234567{i%10}',
                description=f'Deliciosa comida en {restaurant_names[i % len(restaurant_names)]}',
                email=f'restaurant{i+1}@example.com',
                owner=users[i % len(users)]
            )
            restaurants.append(restaurant)
        
        return restaurants

    def create_menu_items(self, restaurants):
        """Crea items del menú para cada restaurante."""
        self.stdout.write('Creando items del menú...')
        
        menu_items = {
            MenuItemCategory.APPETIZER: [
                ('Nachos', 'Nachos con queso y jalapeños', 12000),
                ('Alitas de Pollo', '6 alitas BBQ picantes', 18000),
                ('Ensalada César', 'Ensalada fresca con aderezo césar', 15000),
            ],
            MenuItemCategory.MAIN: [
                ('Hamburguesa Clásica', 'Hamburguesa de carne con papas', 25000),
                ('Pizza Margherita', 'Pizza tradicional italiana', 28000),
                ('Sushi Roll', 'Roll de salmón y aguacate', 22000),
                ('Pasta Carbonara', 'Pasta con salsa carbonara', 24000),
            ],
            MenuItemCategory.DESSERT: [
                ('Tiramisú', 'Postre italiano tradicional', 12000),
                ('Cheesecake', 'Torta de queso con frutos rojos', 14000),
            ],
            MenuItemCategory.DRINK: [
                ('Coca Cola', 'Refresco 350ml', 5000),
                ('Jugo Natural', 'Jugo de naranja natural', 8000),
                ('Cerveza', 'Cerveza nacional 330ml', 7000),
            ]
        }
        
        for restaurant in restaurants:
            for category, items in menu_items.items():
                for name, description, price in items:
                    MenuItem.objects.create(
                        restaurant=restaurant,
                        name=f'{name} - {restaurant.name}',
                        description=description,
                        price=Decimal(str(price)),
                        category=category,
                        preparation_time=15 + (hash(name) % 30)  # 15-45 mins
                    )

    def create_orders(self, count, users, restaurants):
        """Crea órdenes de prueba."""
        self.stdout.write(f'Creando {count} órdenes...')
        orders = []
        
        statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
            OrderStatus.READY,
            OrderStatus.DELIVERED
        ]
        
        for i in range(count):
            restaurant = restaurants[i % len(restaurants)]
            user = users[i % len(users)]
            
            order = Order.objects.create_order(
                user=user,
                restaurant=restaurant,
                delivery_address=f'Calle {i+1} # {i+10}-{i+20}',
                phone_number=user.phone,
                status=statuses[i % len(statuses)]
            )
            
            # Agregar items a la orden
            menu_items = restaurant.menu_items.all()[:3]  # Max 3 items por orden
            
            for menu_item in menu_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=(i % 3) + 1,
                    unit_price=menu_item.price
                )
            
            # Recalcular totales
            order.calculate_totals()
            order.save()
            
            orders.append(order)
        
        return orders

    def create_reviews(self, orders):
        """Crea reviews para órdenes entregadas."""
        self.stdout.write('Creando reviews...')
        
        delivered_orders = [o for o in orders if o.status == OrderStatus.DELIVERED]
        
        comments = [
            'Excelente comida, muy recomendado',
            'Buena calidad y servicio rápido',
            'Delicioso, volveré a pedir',
            'Cumplió mis expectativas',
            'Muy rico todo, gracias'
        ]
        
        for i, order in enumerate(delivered_orders):
            if i % 2 == 0:  # Solo 50% de reviews
                Review.objects.create(
                    order=order,
                    rating=(i % 5) + 1,  # Rating 1-5
                    comment=comments[i % len(comments)]
                )