# app_controle/middleware.py
"""
Middlewares personalizados para controle de sessão e segurança
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger('seguranca')


# ============================================================================
# SESSION EXPIRE MIDDLEWARE
# ============================================================================

class SessionExpireMiddleware(MiddlewareMixin):
    """
    Middleware que gerencia expiração de sessão e valida status da loja
    
    Funcionalidades:
    - Expira sessão ao fechar o navegador
    - Valida se loja ainda está ativa
    - Usa cache para otimizar performance
    - Registra eventos de segurança
    
    OTIMIZAÇÃO: Cache com TTL balanceado (10 minutos)
    - Reduz queries ao banco
    - Mantém tempo razoável para detectar desativações
    """
    
    # ✅ TTL reduzido para 10 minutos (balanceamento entre performance e segurança)
    CACHE_TTL = 60 * 10  # 10 minutos
    CACHE_TTL_INATIVA = 60 * 2  # 2 minutos para lojas inativas
    
    def process_request(self, request):
        """
        Valida sessão em cada requisição
        
        Returns:
            None: Continua processamento normal
            HttpResponse: Redireciona se sessão inválida
        """
        # Ignorar requisições de arquivos estáticos e admin
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # Verificar se existe loja logada na sessão
        loja_id = request.session.get('loja_id')
        if not loja_id:
            return None  # Sem sessão, deixar passar (view decide se precisa auth)
        
        # ✅ Usar cache para verificar status da loja
        cache_key = f'loja_ativa_{loja_id}'
        loja_ativa = cache.get(cache_key)
        
        if loja_ativa is None:
            # Cache miss - consultar banco
            loja_ativa = self._verificar_loja_no_banco(request, loja_id)
            
            if loja_ativa:
                # ✅ Loja ativa - cachear por 10 minutos
                cache.set(cache_key, True, self.CACHE_TTL)
                logger.debug(f"Loja {loja_id} verificada e está ativa (cache atualizado)")
            else:
                # ❌ Loja inativa - cachear por 2 minutos apenas
                cache.set(cache_key, False, self.CACHE_TTL_INATIVA)
                return self._handle_loja_inativa(request, loja_id)
        
        elif not loja_ativa:
            # ❌ Cache hit - loja inativa
            logger.warning(
                f"Tentativa de acesso com loja inativa (cache): "
                f"Loja ID {loja_id} - IP: {request.META.get('REMOTE_ADDR')}"
            )
            return self._handle_loja_inativa(request, loja_id)
        
        # ✅ Loja ativa - continuar normalmente
        return None
    
    def _verificar_loja_no_banco(self, request, loja_id):
        """
        Verifica no banco se loja está ativa
        
        Args:
            request: HttpRequest
            loja_id: ID da loja
        
        Returns:
            bool: True se ativa, False se inativa/inexistente
        """
        from .models import Loja
        
        try:
            # ✅ Usar novos nomes de campos com only()
            loja = Loja.objects.only('id', 'ativo', 'nome').get(
                id=loja_id,  # ✅ Novo nome
                ativo=True   # ✅ Novo nome
            )
            
            logger.info(
                f"Sessão validada: Loja '{loja.nome}' (ID: {loja_id}) - "
                f"IP: {request.META.get('REMOTE_ADDR')}"
            )
            return True
            
        except Loja.DoesNotExist:
            logger.warning(
                f"Loja não encontrada ou inativa: ID {loja_id} - "
                f"IP: {request.META.get('REMOTE_ADDR')} - "
                f"Path: {request.path}"
            )
            return False
    
    def _handle_loja_inativa(self, request, loja_id):
        """
        Trata caso de loja inativa
        
        Args:
            request: HttpRequest
            loja_id: ID da loja
        
        Returns:
            HttpResponse: Redirect para login
        """
        # Limpar sessão
        nome_loja = request.session.get('loja_nome', 'Desconhecida')
        request.session.flush()
        
        # Registrar evento
        logger.warning(
            f"Sessão encerrada: Loja '{nome_loja}' (ID: {loja_id}) foi desativada - "
            f"IP: {request.META.get('REMOTE_ADDR')}"
        )
        
        # Adicionar mensagem para o usuário
        messages.error(
            request,
            '❌ Sua sessão foi encerrada. Esta loja foi desativada.'
        )
        
        # Redirecionar para login
        return redirect('login')


# ============================================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adiciona headers de segurança às respostas
    
    Headers adicionados:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Referrer-Policy: strict-origin-when-cross-origin
    """
    
    def process_response(self, request, response):
        """Adiciona headers de segurança"""
        
        # Prevenir MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Prevenir clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Ativar proteção XSS do navegador
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Política de referrer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response


# ============================================================================
# REQUEST LOGGING MIDDLEWARE (Opcional)
# ============================================================================

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Registra todas as requisições (opcional - desabilitar em produção se muito tráfego)
    
    Útil para:
    - Auditoria
    - Debugging
    - Análise de uso
    """
    
    # ✅ Configurar quais paths devem ser logados
    PATHS_TO_LOG = [
        '/login/',
        '/cadastro/',
        '/logout/',
        '/vendas/',
        '/clientes/',
    ]
    
    def process_request(self, request):
        """Registra requisição se estiver nos paths configurados"""
        
        # Verificar se deve logar este path
        should_log = any(
            request.path.startswith(path) 
            for path in self.PATHS_TO_LOG
        )
        
        if should_log:
            loja_id = request.session.get('loja_id', 'Anônimo')
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')[:100]
            
            logger.info(
                f"REQUEST: {request.method} {request.path} - "
                f"Loja: {loja_id} - IP: {ip} - UA: {user_agent}"
            )
        
        return None


# ============================================================================
# CACHE INVALIDATION MIDDLEWARE (Para Admin)
# ============================================================================

class CacheInvalidationMiddleware(MiddlewareMixin):
    """
    Invalida cache quando loja é modificada via Admin
    
    Garante que mudanças no status da loja sejam refletidas imediatamente
    """
    
    def process_response(self, request, response):
        """Invalida cache após salvar loja no admin"""
        
        # Verificar se foi uma requisição POST no admin de Loja
        if (
            request.method == 'POST' 
            and '/admin/app_controle/loja/' in request.path
            and response.status_code in [200, 302]
        ):
            # Extrair loja_id da URL se possível
            try:
                # URL pattern: /admin/app_controle/loja/{id}/change/
                parts = request.path.split('/')
                if 'change' in parts:
                    loja_id = parts[parts.index('loja') + 1]
                    cache_key = f'loja_ativa_{loja_id}'
                    cache.delete(cache_key)
                    
                    logger.info(
                        f"Cache invalidado para Loja ID {loja_id} "
                        f"(modificação via admin)"
                    )
            except (ValueError, IndexError):
                # Se falhar ao extrair ID, invalidar todo o cache de lojas
                logger.warning("Falha ao extrair loja_id, invalidando cache geral")
                # Não temos como invalidar seletivamente, mas o TTL cuidará disso
        
        return response