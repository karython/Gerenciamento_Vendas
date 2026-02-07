# app_controle/views/health_views.py
"""
Health Check Views - Endpoints para monitoramento
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check completo com verificação de banco
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check - Erro no BD: {e}", exc_info=True)
        db_status = "unhealthy"
    
    response_data = {
        "status": "ok" if db_status == "healthy" else "error",
        "database": db_status,
        "environment": "production" if not settings.DEBUG else "development"
    }
    
    status_code = 200 if db_status == "healthy" else 500
    logger.info(f"Health check - Status: {response_data['status']}")
    
    return JsonResponse(response_data, status=status_code)


@require_http_methods(["GET"])
def health_check_simple(request):
    """
    Health check simples para keep-alive
    """
    return JsonResponse({"status": "alive"}, status=200)