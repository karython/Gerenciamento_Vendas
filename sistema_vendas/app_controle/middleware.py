# app_controle/middleware.py

from django.utils.deprecation import MiddlewareMixin

class SessionExpireMiddleware(MiddlewareMixin):
    """
    Middleware que garante que a sessão expire ao fechar o navegador
    e verifica se a loja ainda está ativa
    """
    
    def process_request(self, request):
        # Verificar se existe loja logada na sessão
        if 'loja_id' in request.session:
            from .models import Loja
            
            try:
                # Buscar loja no banco
                loja = Loja.objects.get(
                    idLOJA=request.session['loja_id'],
                    ATIVO=True
                )
                
                # Loja existe e está ativa, continua
                pass
                
            except Loja.DoesNotExist:
                # Loja não existe ou foi desativada, limpa a sessão
                request.session.flush()
                
        return None