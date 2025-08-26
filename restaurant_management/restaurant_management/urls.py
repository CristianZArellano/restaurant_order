"""
URL configuration for restaurant_management project.
"""
from django.contrib import admin
from django.urls import path, include

# Configuración del admin
admin.site.site_header = 'Sistema de Gestión de Restaurantes'
admin.site.site_title = 'Administración'
admin.site.index_title = 'Panel de Administración'

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    
    # API endpoints
    path("api/auth/", include('users.urls')),
    # path("api/restaurants/", include('restaurants.urls')),
    # path("api/orders/", include('orders.urls')),
]
