# app_controle/utils/security.py
"""
Utilitários de segurança: Rate limiting, validação de força de senha, etc.
"""

import logging
import re
from django.core.cache import cache
from django.contrib import messages
from functools import wraps

logger = logging.getLogger('seguranca')


class RateLimiter:
    """
    Rate limiter para proteger contra brute force.
    Limita tentativas de login por IP e por CNPJ.
    """
    
    MAX_ATTEMPTS = 5  # Máximo de tentativas
    LOCKOUT_TIME = 900  # 15 minutos em segundos
    
    @staticmethod
    def check_rate_limit(identifier, request=None):
        """
        Verifica se está dentro do rate limit.
        
        Args:
            identifier: chave única (ex: CNPJ ou IP)
            request: objeto da requisição (para pegar IP)
        
        Returns:
            tuple: (está_permitido: bool, tentativas_restantes: int)
        """
        cache_key = f'rate_limit_{identifier}'
        tentativas = cache.get(cache_key, 0)
        
        ip = request.META.get('REMOTE_ADDR') if request else 'unknown'
        
        if tentativas >= RateLimiter.MAX_ATTEMPTS:
            logger.warning(
                f"Rate limit atingido para {identifier} - IP: {ip} - "
                f"Tentativas: {tentativas}/{RateLimiter.MAX_ATTEMPTS}"
            )
            return False, 0
        
        return True, RateLimiter.MAX_ATTEMPTS - tentativas
    
    @staticmethod
    def increment_attempts(identifier, request=None):
        """Incrementa o contador de tentativas."""
        cache_key = f'rate_limit_{identifier}'
        tentativas = cache.get(cache_key, 0) + 1
        cache.set(cache_key, tentativas, RateLimiter.LOCKOUT_TIME)
        
        ip = request.META.get('REMOTE_ADDR') if request else 'unknown'
        logger.warning(
            f"Tentativa de login falhada para {identifier} - IP: {ip} - "
            f"Tentativas: {tentativas}/{RateLimiter.MAX_ATTEMPTS}"
        )
    
    @staticmethod
    def reset_attempts(identifier, request=None):
        """Reseta o contador de tentativas após login bem-sucedido."""
        cache_key = f'rate_limit_{identifier}'
        cache.delete(cache_key)
        
        ip = request.META.get('REMOTE_ADDR') if request else 'unknown'
        logger.info(f"Login bem-sucedido para {identifier} - IP: {ip}")


class ValidadorSenha:
    """Validação de força de senha."""
    
    MIN_LENGTH = 12
    REQUER_MAIUSCULA = True
    REQUER_MINUSCULA = True
    REQUER_NUMERO = True
    REQUER_ESPECIAL = True
    
    @staticmethod
    def validar(senha):
        """
        Valida a força da senha.
        
        Returns:
            tuple: (válida: bool, mensagem: str)
        """
        if len(senha) < ValidadorSenha.MIN_LENGTH:
            return False, f"Mínimo {ValidadorSenha.MIN_LENGTH} caracteres"
        
        if ValidadorSenha.REQUER_MAIUSCULA and not re.search(r'[A-Z]', senha):
            return False, "Deve conter pelo menos uma letra maiúscula"
        
        if ValidadorSenha.REQUER_MINUSCULA and not re.search(r'[a-z]', senha):
            return False, "Deve conter pelo menos uma letra minúscula"
        
        if ValidadorSenha.REQUER_NUMERO and not re.search(r'[0-9]', senha):
            return False, "Deve conter pelo menos um número"
        
        if ValidadorSenha.REQUER_ESPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
            return False, "Deve conter pelo menos um caractere especial (!@#$%^&*)"
        
        return True, "Senha forte"


class ValidadorCNPJ:
    """Validação completa de CNPJ incluindo algoritmo de verificação."""
    
    @staticmethod
    def validar(cnpj):
        """
        Valida CNPJ pelo algoritmo de verificação.
        
        Returns:
            bool: CNPJ válido
        """
        import re
        
        cnpj = re.sub(r'\D', '', cnpj)
        
        if len(cnpj) != 14:
            return False
        
        # Evitar CNPJs óbvios inválidos
        if cnpj == cnpj[0] * 14:
            return False
        
        # Primeiro dígito verificador
        soma = sum(int(cnpj[i]) * (5 - (i % 4)) for i in range(8))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        if int(cnpj[8]) != dv1:
            return False
        
        # Segundo dígito verificador
        soma = sum(int(cnpj[i]) * (6 - (i % 4)) for i in range(8, 12))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        return int(cnpj[9]) == dv2


def requer_login(view_func):
    """
    Decorator para proteger views que requerem autenticação.
    Redireciona para login se não estiver autenticado.
    """
    from functools import wraps
    from django.shortcuts import redirect
    from ..services.auth_services import AuthService
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        loja = AuthService.loja_logada(request)
        if not loja:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            logger.warning(f"Tentativa de acesso sem autenticação - IP: {ip} - Path: {request.path}")
            messages.warning(request, "Você precisa estar logado para acessar esta página.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    
    return wrapper
