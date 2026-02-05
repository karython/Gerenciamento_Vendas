"""
Health Check Views - Endpoints para monitoramento e keep-alive
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
    Endpoint de health check para monitorar se o servidor está ativo.
    Verifica conectividade com banco de dados e retorna status geral.
    
    Resposta 200: Sistema operacional
    Resposta 500: Erro no sistema
    
    Exemplo: GET /health/
    """
    try:
        # Testa conexão com banco de dados
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check - Erro no banco de dados: {e}")
        db_status = "unhealthy"
    
    # Monta resposta
    response_data = {
        "status": "ok" if db_status == "healthy" else "error",
        "database": db_status,
        "debug": settings.DEBUG,
        "environment": "production" if not settings.DEBUG else "development"
    }
    
    status_code = 200 if db_status == "healthy" else 500
    
    logger.info(f"Health check solicitado - Status: {response_data['status']}")
    
    return JsonResponse(response_data, status=status_code)


@require_http_methods(["GET"])
def health_check_simple(request):
    """
    Versão simples do health check - apenas retorna OK.
    Mais leve para uso frequente (keep-alive).
    
    Exemplo: GET /health/ping/
    """
    logger.debug("Keep-alive ping recebido")
    return JsonResponse({"status": "alive"}, status=200)
