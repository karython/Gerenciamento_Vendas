"""
Middleware para registrar tempo de requisições HTTP
Adicione este middleware ao settings.py para monitorar requisições
"""

import time
import logging
from django.utils.deprecation import MiddlewareNotUsed
from django.db import connection, reset_queries
from django.test.utils import override_settings

logger = logging.getLogger(__name__)

class QueryCounterMiddleware:
    """
    Middleware que registra todas as queries executadas em uma requisição
    e o tempo total gasto.
    
    Adicione ao settings.py:
    MIDDLEWARE = [
        ...
        'app_controle.middleware.QueryCounterMiddleware',
        ...
    ]
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Desabilitar se não em DEBUG
        from django.conf import settings
        if not settings.DEBUG:
            raise MiddlewareNotUsed("QueryCounterMiddleware apenas em DEBUG")
    
    def __call__(self, request):
        # Começar rastreamento
        reset_queries()
        request.start_time = time.time()
        
        # Executar view
        response = self.get_response(request)
        
        # Calcular métricas
        request.end_time = time.time()
        request.total_time = (request.end_time - request.start_time) * 1000
        request.num_queries = len(connection.queries)
        request.db_time = sum(float(q.get('time', 0)) for q in connection.queries) * 1000
        
        # Registrar informações
        self._log_request_info(request, response)
        
        # Adicionar headers informativos (opcional)
        if hasattr(response, '__setitem__'):
            response['X-DB-Query-Count'] = str(request.num_queries)
            response['X-DB-Time'] = f"{request.db_time:.2f}ms"
            response['X-Total-Time'] = f"{request.total_time:.2f}ms"
        
        return response
    
    def _log_request_info(self, request, response):
        """Registrar informações da requisição"""
        
        path = request.path
        method = request.method
        status = response.status_code
        num_queries = request.num_queries
        db_time = request.db_time
        total_time = request.total_time
        
        # Determinar nível de severidade
        if total_time > 1000:  # > 1 segundo
            level = logging.WARNING
            icon = "🔴"
        elif total_time > 500:  # > 500ms
            level = logging.INFO
            icon = "🟡"
        else:
            level = logging.DEBUG
            icon = "✅"
        
        message = (
            f"{icon} {method} {path} [{status}] | "
            f"Queries: {num_queries} | "
            f"DB: {db_time:.2f}ms | "
            f"Total: {total_time:.2f}ms"
        )
        
        logger.log(level, message)
        
        # Se muito lento, listar todas as queries
        if total_time > 1000 and connection.queries:
            logger.warning(f"  Queries lenta executadas para {path}:")
            for idx, query in enumerate(connection.queries, 1):
                q_time = float(query.get('time', 0)) * 1000
                sql = query['sql'][:100]
                logger.warning(f"    {idx}. [{q_time:.2f}ms] {sql}...")


class SlowQueryMiddleware:
    """
    Middleware que alerta sobre queries lentas individuais
    
    SLOW_QUERY_THRESHOLD = 0.1  # 100ms
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        from django.conf import settings
        if not settings.DEBUG:
            raise MiddlewareNotUsed("SlowQueryMiddleware apenas em DEBUG")
        
        self.threshold = getattr(settings, 'SLOW_QUERY_THRESHOLD', 0.1)
    
    def __call__(self, request):
        reset_queries()
        response = self.get_response(request)
        
        # Encontrar queries lentas
        slow_queries = [
            q for q in connection.queries
            if float(q.get('time', 0)) > self.threshold
        ]
        
        if slow_queries:
            logger.warning(
                f"⚠️  {len(slow_queries)} queries lentas em {request.path}"
            )
            for query in slow_queries:
                q_time = float(query.get('time', 0)) * 1000
                sql = query['sql'][:150]
                logger.warning(f"   [{q_time:.2f}ms] {sql}...")
        
        return response


# ============================================================================
# UTILITÁRIOS PARA TESTAR QUERIES
# ============================================================================

class QueryProfiler:
    """
    Utilitário para perfilar queries em testes ou desenvolvimento
    
    Uso:
        from app_controle.middleware import QueryProfiler
        
        with QueryProfiler("Teste de busca"):
            usuarios = User.objects.all()
            print(usuarios.count())
    """
    
    def __init__(self, label="Query"):
        self.label = label
        self.queries_count = 0
        self.db_time = 0
    
    def __enter__(self):
        reset_queries()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.queries_count = len(connection.queries)
        self.db_time = sum(float(q.get('time', 0)) for q in connection.queries)
        
        print(f"\n{'='*70}")
        print(f"📊 {self.label}")
        print(f"{'='*70}")
        print(f"Queries executadas: {self.queries_count}")
        print(f"Tempo no BD: {self.db_time:.4f}s ({self.db_time * 1000:.2f}ms)")
        
        if self.queries_count <= 5:
            print(f"\nQueries:")
            for idx, query in enumerate(connection.queries, 1):
                q_time = float(query.get('time', 0))
                sql = query['sql']
                if len(sql) > 100:
                    sql = sql[:100] + "..."
                print(f"  {idx}. [{q_time:.4f}s] {sql}")
        
        print(f"{'='*70}\n")


# ============================================================================
# EXEMPLO DE USO EM TESTES
# ============================================================================

def exemplo_uso_middleware():
    """
    Exemplo de como usar os utilitários
    """
    from django.test import TestCase, override_settings
    from django.db import connection, reset_queries
    
    class PerformanceTests(TestCase):
        """Testes de performance com monitoramento"""
        
        @override_settings(DEBUG=True)
        def test_lista_lojas_performance(self):
            """Verificar performance de listar lojas"""
            from QueryProfiler import QueryProfiler
            from app_controle.models import Loja
            
            with QueryProfiler("Listar Lojas") as profiler:
                lojas = list(Loja.objects.all())
            
            # Assertions
            self.assertLess(profiler.queries_count, 2)
            self.assertLess(profiler.db_time, 0.1)  # < 100ms
        
        @override_settings(DEBUG=True)
        def test_venda_com_cliente(self):
            """Verificar N+1 queries"""
            from QueryProfiler import QueryProfiler
            from app_controle.models import Venda
            
            # ❌ SEM otimização
            with QueryProfiler("Venda SEM select_related") as profiler_bad:
                for venda in Venda.objects.all():
                    _ = venda.CLIENTE_idCLIENTE.NOME_CLIENTE
            
            # ✅ COM otimização
            with QueryProfiler("Venda COM select_related") as profiler_good:
                for venda in Venda.objects.select_related('CLIENTE_idCLIENTE'):
                    _ = venda.CLIENTE_idCLIENTE.NOME_CLIENTE
            
            # A versão otimizada deve ter MUITO menos queries
            self.assertLess(
                profiler_good.queries_count,
                profiler_bad.queries_count
            )


if __name__ == '__main__':
    print("Exemplo de uso do QueryProfiler:")
    
    from app_controle.models import Loja
    
    # Exemplo 1: Query normal
    with QueryProfiler("Loja.objects.all()"):
        lojas = list(Loja.objects.all())
    
    # Exemplo 2: Query otimizada
    with QueryProfiler("Loja.objects.only(...)"):
        lojas = list(Loja.objects.only('idLOJA', 'NOME_LOJA'))
