# Sistema de Gestión de Pedidos para Restaurantes

Un sistema completo de gestión de pedidos para restaurantes desarrollado con Django y Django REST Framework, aplicando principios SOLID, LEAN Code y mejores prácticas de desarrollo.

## 🚀 Características Principales

### Funcionalidades Core
- **Sistema de Usuarios**: Registro, autenticación y gestión de perfiles
- **Gestión de Restaurantes**: CRUD completo con información detallada
- **Sistema de Menús**: Categorización y gestión de elementos del menú
- **Sistema de Órdenes**: Flujo completo desde creación hasta entrega
- **Sistema de Reviews**: Calificaciones y comentarios
- **API REST**: Endpoints completos con autenticación por token
- **Panel de Administración**: Interfaz optimizada para gestión

### Características Técnicas
- **Arquitectura LEAN**: Código refactorizado eliminando duplicación
- **Principios SOLID**: Separación de responsabilidades y bajo acoplamiento
- **Validaciones Robustas**: Validadores personalizados reutilizables
- **Managers Personalizados**: Optimización de consultas ORM
- **Middleware Personalizado**: Logging, rate limiting y seguridad
- **Tests Unitarios**: Cobertura completa de modelos y funcionalidades
- **Comandos de Management**: Herramientas administrativas personalizadas

## 🏗️ Arquitectura del Sistema

### Aplicaciones

#### `core/`
Componentes reutilizables y utilidades:
- **Validators**: Validadores personalizados (teléfono, decimales, ratings)
- **Models**: Mixins base (TimestampedModel, ActiveModel, SlugModel)
- **Managers**: Managers personalizados para optimización de queries
- **Middleware**: Logging, rate limiting, seguridad, optimización DB
- **Serializers**: Serializers base para la API

#### `users/`
Sistema de usuarios personalizado:
- **CustomUser**: Modelo extendido con teléfono y verificación
- **API**: Registro, login, logout, perfil, cambio de contraseña
- **Validaciones**: Email único, teléfono internacional
- **Properties**: Contadores de restaurantes y órdenes

#### `restaurants/`
Gestión de restaurantes:
- **Restaurant**: Modelo con slug automático y validaciones
- **Managers**: Búsqueda, filtros por owner, estadísticas
- **Properties**: Contadores de menú, órdenes, calificaciones
- **Validaciones**: Nombre único, email formato, teléfono

#### `orders/`
Sistema completo de órdenes:
- **MenuItem**: Elementos del menú con categorías
- **Order**: Órdenes con cálculo automático de totales
- **OrderItem**: Items individuales con precios fijos
- **OrderStatusHistory**: Trazabilidad de cambios de estado
- **Review**: Sistema de calificaciones 1-5 estrellas

### Modelos de Datos Optimizados

```python
# Jerarquía de modelos con mixins
CustomUser(AbstractUser, TimestampedModel)
Restaurant(TimestampedModel, ActiveModel, SlugModel)
MenuItem(TimestampedModel, ActiveModel)
Order(TimestampedModel)
```

### Estados de Orden
```
PENDING → CONFIRMED → PREPARING → READY → OUT_FOR_DELIVERY → DELIVERED
                                     ↓
                                 CANCELLED
```

## 🛠️ Instalación y Configuración

### Requisitos Previos
- Python 3.8+
- Django 5.2.5
- PostgreSQL (producción) / SQLite (desarrollo)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/CristianZArellano/restaurant_order.git
cd restaurant_orderV2

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos
cd restaurant_management
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear datos de prueba (opcional)
python manage.py create_sample_data --users 10 --restaurants 5 --orders 20

# Ejecutar servidor de desarrollo
python manage.py runserver
```

## 📊 Comandos de Management

### Crear Datos de Prueba
```bash
python manage.py create_sample_data --users 20 --restaurants 10 --orders 50 --clear
```

### Generar Reportes
```bash
# Reporte resumen
python manage.py generate_report --type summary --days 30

# Reporte de restaurantes
python manage.py generate_report --type restaurants --days 7

# Reporte de órdenes
python manage.py generate_report --type orders --days 1

# Reporte de usuarios
python manage.py generate_report --type users --days 30
```

### Limpieza de Datos
```bash
# Vista previa de limpieza
python manage.py cleanup_old_data --days 90 --dry-run

# Ejecutar limpieza
python manage.py cleanup_old_data --days 90
```

## 🔌 API REST Endpoints

### Autenticación
```
POST /api/auth/register/          - Registro de usuario
POST /api/auth/login/             - Login
POST /api/auth/logout/            - Logout
GET  /api/auth/profile/           - Obtener perfil
PUT  /api/auth/profile/update/    - Actualizar perfil
POST /api/auth/change-password/   - Cambiar contraseña
```

### Restaurantes
```
GET    /api/restaurants/           - Listar restaurantes
POST   /api/restaurants/           - Crear restaurante
GET    /api/restaurants/{id}/      - Detalle restaurante
PUT    /api/restaurants/{id}/      - Actualizar restaurante
DELETE /api/restaurants/{id}/      - Eliminar restaurante
GET    /api/restaurants/{id}/menu/ - Menú del restaurante
```

### Órdenes
```
GET    /api/orders/                - Listar órdenes del usuario
POST   /api/orders/                - Crear orden
GET    /api/orders/{id}/           - Detalle de orden
PUT    /api/orders/{id}/           - Actualizar orden
GET    /api/orders/{id}/status/    - Historial de estados
POST   /api/orders/{id}/review/    - Crear review
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
python manage.py test

# Tests específicos
python manage.py test users.tests
python manage.py test restaurants.tests
python manage.py test orders.tests
python manage.py test core.tests

# Con coverage
coverage run --source='.' manage.py test
coverage report
```

### Estructura de Tests
- **Core**: Tests de validadores y utilidades
- **Users**: Tests de modelo CustomUser y API
- **Restaurants**: Tests de modelo Restaurant y managers
- **Orders**: Tests de modelos de órdenes y lógica de negocio

## 🔧 Configuración Avanzada

### Variables de Entorno (.env)
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Settings por Ambiente
- **Development**: SQLite, logging console, debug toolbar
- **Production**: PostgreSQL, Redis cache, security headers

### Middleware Personalizado
```python
MIDDLEWARE = [
    'core.middleware.SecurityHeadersMiddleware',      # Headers de seguridad
    'core.middleware.RequestLoggingMiddleware',       # Logging de requests
    'core.middleware.RateLimitMiddleware',            # Rate limiting
    'core.middleware.APIVersionMiddleware',           # Versionado de API
    'core.middleware.DatabaseOptimizationMiddleware', # Optimización DB
]
```

## 📈 Optimizaciones Implementadas

### Base de Datos
- **Índices**: Optimizados para consultas frecuentes
- **Select/Prefetch Related**: Reducción de queries N+1
- **Managers Personalizados**: Queries optimizadas por caso de uso
- **Agregaciones**: Cálculos eficientes de estadísticas

### Caching
- **Cache de Sesiones**: Redis backend
- **Cache de Views**: Para datos estáticos
- **Cache de Queries**: Para consultas repetitivas

### API Performance
- **Paginación**: 20 elementos por página por defecto
- **Filtros**: django-filter integration
- **Throttling**: Rate limiting por usuario/anónimo
- **Serializers Optimizados**: Solo campos necesarios

## 🛡️ Seguridad

### Medidas Implementadas
- **Token Authentication**: REST API segura
- **Rate Limiting**: Protección contra spam
- **Security Headers**: XSS, CSRF, Clickjacking protection
- **Input Validation**: Validadores robustos
- **Password Validation**: Django password validators
- **HTTPS Ready**: Configuración para producción

### Headers de Seguridad
```python
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

## 📱 Uso de la API

### Registro y Autenticación
```javascript
// Registro
POST /api/auth/register/
{
    "username": "usuario123",
    "email": "usuario@example.com",
    "password": "contraseña123",
    "password_confirm": "contraseña123",
    "first_name": "Juan",
    "last_name": "Pérez"
}

// Login
POST /api/auth/login/
{
    "username": "usuario123",
    "password": "contraseña123"
}

// Headers para requests autenticados
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Crear Orden
```javascript
POST /api/orders/
{
    "restaurant": 1,
    "order_type": "DELIVERY",
    "delivery_address": "Calle 123 #45-67",
    "phone_number": "+573001234567",
    "items": [
        {
            "menu_item": 1,
            "quantity": 2,
            "special_instructions": "Sin cebolla"
        },
        {
            "menu_item": 3,
            "quantity": 1
        }
    ]
}
```

## 🚀 Deployment

### Producción con Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "restaurant_management.wsgi:application"]
```

### Variables de Producción
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-production-secret-key
```

## 📝 Logs y Monitoreo

### Estructura de Logs
```
INFO  - Request started: GET /api/orders/ | User: juan123 | IP: 192.168.1.1
INFO  - Request completed: GET /api/orders/ | Status: 200 | Duration: 0.045s
WARN  - Slow request detected: GET /api/restaurants/ | Duration: 2.150s
ERROR - Unhandled exception in POST /api/orders/: ValidationError
```

### Métricas Disponibles
- Tiempo de respuesta por endpoint
- Número de queries por request
- Rate limiting violations
- Errores 4xx/5xx
- Usuarios activos

## 🤝 Contribución

### Estándares de Código
- **PEP 8**: Estilo de código Python
- **Black**: Formateo automático
- **isort**: Importaciones ordenadas
- **Flake8**: Linting
- **Docstrings**: Documentación de funciones

### Flujo de Desarrollo
1. Fork del repositorio
2. Crear branch feature/bugfix
3. Escribir tests
4. Implementar funcionalidad
5. Ejecutar tests y linting
6. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- 📧 Email: soporte@restaurant-system.com
- 📖 Documentación: [docs.restaurant-system.com]
- 🐛 Issues: GitHub Issues

---

**Desarrollado con ❤️ aplicando principios SOLID y Clean Code**
