"""
Middleware personalizado para logging, manejo de errores y optimizaciones.
"""

import logging
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger("restaurant_management")


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging de requests y performance monitoring.
    """

    def process_request(self, request):
        """Procesa el request y inicia el timer."""
        request.start_time = time.time()

        # Log basic request info
        user_info = "Anonymous"
        if hasattr(request, "user") and not isinstance(request.user, AnonymousUser):
            user_info = f"{request.user.username} (ID: {request.user.id})"

        logger.info(
            f"Request started: {request.method} {request.path} | "
            f"User: {user_info} | IP: {self._get_client_ip(request)}"
        )

    def process_response(self, request, response):
        """Procesa la respuesta y calcula tiempo de procesamiento."""
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time

            # Log response info
            logger.info(
                f"Request completed: {request.method} {request.path} | "
                f"Status: {response.status_code} | Duration: {duration:.3f}s"
            )

            # Alertar sobre requests lentos
            if duration > 2.0:  # Más de 2 segundos
                logger.warning(
                    f"Slow request detected: {request.method} {request.path} | "
                    f"Duration: {duration:.3f}s"
                )

        return response

    def process_exception(self, request, exception):
        """Procesa excepciones no manejadas."""
        logger.error(
            f"Unhandled exception in {request.method} {request.path}: "
            f"{type(exception).__name__}: {str(exception)}",
            exc_info=True,
        )

        # En desarrollo, dejar que Django maneje la excepción
        # En producción, podríamos retornar una respuesta JSON elegante
        return None

    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware simple de rate limiting por IP.
    """

    def process_request(self, request):
        """Aplica rate limiting básico."""
        ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{ip}"

        # Permitir más requests para usuarios autenticados
        if hasattr(request, "user") and not isinstance(request.user, AnonymousUser):
            max_requests = 1000  # 1000 requests por hora para usuarios autenticados
        else:
            max_requests = 100  # 100 requests por hora para anónimos

        current_requests = cache.get(cache_key, 0)

        if current_requests >= max_requests:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return JsonResponse(
                {"error": "Rate limit exceeded. Please try again later."}, status=429
            )

        # Incrementar contador
        cache.set(cache_key, current_requests + 1, 3600)  # 1 hora TTL
        return None

    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad.
    """

    def process_response(self, request, response):
        """Agrega headers de seguridad a la respuesta."""
        # Prevenir clickjacking
        response["X-Frame-Options"] = "DENY"

        # Prevenir MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # Habilitar XSS protection
        response["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Para APIs, agregar CORS headers si es necesario
        if request.path.startswith("/api/"):
            response["Access-Control-Allow-Origin"] = (
                "*"  # Configurar según necesidades
            )
            response["Access-Control-Allow-Methods"] = (
                "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            )
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response


class DatabaseOptimizationMiddleware(MiddlewareMixin):
    """
    Middleware para optimización de base de datos y debugging.
    """

    def process_request(self, request):
        """Inicializa contadores de queries."""
        if hasattr(self, "debug_queries"):
            from django.db import reset_queries

            reset_queries()

    def process_response(self, request, response):
        """Reporta estadísticas de queries de base de datos."""
        if hasattr(self, "debug_queries"):
            from django.db import connection

            query_count = len(connection.queries)
            if query_count > 10:  # Alertar sobre muchas queries
                logger.warning(
                    f"High query count detected: {query_count} queries in "
                    f"{request.method} {request.path}"
                )

                # En development, loggear queries lentas
                slow_queries = [
                    q
                    for q in connection.queries
                    if float(q["time"]) > 0.1  # > 100ms
                ]

                for query in slow_queries:
                    logger.warning(
                        f"Slow query ({query['time']}s): {query['sql'][:200]}..."
                    )

        return response


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware para manejo de versiones de API.
    """

    def process_request(self, request):
        """Procesa versión de API desde headers."""
        if request.path.startswith("/api/"):
            # Obtener versión desde header o usar default
            api_version = request.META.get("HTTP_API_VERSION", "v1")
            request.api_version = api_version

            # Validar versión soportada
            supported_versions = ["v1"]  # Agregar más versiones según necesidad

            if api_version not in supported_versions:
                return JsonResponse(
                    {
                        "error": f"Unsupported API version: {api_version}",
                        "supported_versions": supported_versions,
                    },
                    status=400,
                )

        return None
