# app_controle/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

class SessionExpireMiddleware(MiddlewareMixin):
    """
    Middleware que garante que a sessão expire ao fechar o navegador
    e verifica se a loja ainda está ativa
    OTIMIZADO: Usa cache para reduzir queries ao banco
    """
    
    def process_request(self, request):
        # Verificar se existe loja logada na sessão
        if 'loja_id' in request.session:
            loja_id = request.session['loja_id']
            
            # Usar cache para verificar se loja está ativa (TTL: 5 minutos)
            cache_key = f'loja_ativa_{loja_id}'
            loja_ativa = cache.get(cache_key)
            
            if loja_ativa is None:
                # Se não está em cache, verificar no banco
                from .models import Loja
                try:
                    loja = Loja.objects.only('idLOJA', 'ATIVO').get(
                        idLOJA=loja_id,
                        ATIVO=True
                    )
                    # Cachear resultado por 5 minutos
                    cache.set(cache_key, True, 60 * 5)
                    loja_ativa = True
                except Loja.DoesNotExist:
                    # Loja não existe ou foi desativada
                    request.session.flush()
                    return None
            elif not loja_ativa:
                # Loja não está mais ativa
                request.session.flush()
                return None
                
        return None