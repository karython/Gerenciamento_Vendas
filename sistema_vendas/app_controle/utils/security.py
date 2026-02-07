# app_controle/utils/security.py
"""
Utilitários de segurança: Rate limiting, validação de senha e CNPJ
"""

import logging
import re
from django.core.cache import cache
from django.contrib import messages

logger = logging.getLogger('seguranca')


# ============================================================================
# RATE LIMITER
# ============================================================================

class RateLimiter:
    """
    Rate limiter para proteger contra brute force.
    Limita tentativas de login por identificador (CNPJ) E por IP.
    """
    
    MAX_ATTEMPTS = 5  # Máximo de tentativas
    LOCKOUT_TIME = 900  # 15 minutos em segundos
    
    @staticmethod
    def check_rate_limit(identifier, request=None):
        """
        Verifica se está dentro do rate limit (por ID e IP)
        
        Args:
            identifier (str): Chave única (ex: CNPJ)
            request (HttpRequest): Objeto da requisição
        
        Returns:
            tuple: (está_permitido: bool, tentativas_restantes: int)
        """
        # Rate limit por identificador
        cache_key_id = f'rate_limit_id_{identifier}'
        tentativas_id = cache.get(cache_key_id, 0)
        
        # ✅ Rate limit por IP (proteção adicional)
        if request:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key_ip = f'rate_limit_ip_{ip}'
            tentativas_ip = cache.get(cache_key_ip, 0)
            
            # Bloquear se qualquer um dos limites for atingido
            if tentativas_id >= RateLimiter.MAX_ATTEMPTS:
                logger.warning(
                    f"Rate limit por identificador atingido: {identifier} - "
                    f"IP: {ip} - Tentativas: {tentativas_id}/{RateLimiter.MAX_ATTEMPTS}"
                )
                return False, 0
            
            if tentativas_ip >= RateLimiter.MAX_ATTEMPTS:
                logger.warning(
                    f"Rate limit por IP atingido: {ip} - "
                    f"Tentando: {identifier} - Tentativas: {tentativas_ip}/{RateLimiter.MAX_ATTEMPTS}"
                )
                return False, 0
            
            # Retornar o menor número de tentativas restantes
            return True, min(
                RateLimiter.MAX_ATTEMPTS - tentativas_id,
                RateLimiter.MAX_ATTEMPTS - tentativas_ip
            )
        
        # Fallback se não houver request (não deveria acontecer)
        if tentativas_id >= RateLimiter.MAX_ATTEMPTS:
            logger.warning(
                f"Rate limit atingido para {identifier} (sem IP) - "
                f"Tentativas: {tentativas_id}/{RateLimiter.MAX_ATTEMPTS}"
            )
            return False, 0
        
        return True, RateLimiter.MAX_ATTEMPTS - tentativas_id
    
    @staticmethod
    def increment_attempts(identifier, request=None):
        """
        Incrementa o contador de tentativas (ID e IP)
        
        Args:
            identifier (str): Chave única
            request (HttpRequest): Objeto da requisição
        """
        # Incrementar por identificador
        cache_key_id = f'rate_limit_id_{identifier}'
        tentativas_id = cache.get(cache_key_id, 0) + 1
        cache.set(cache_key_id, tentativas_id, RateLimiter.LOCKOUT_TIME)
        
        # ✅ Incrementar por IP
        if request:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key_ip = f'rate_limit_ip_{ip}'
            tentativas_ip = cache.get(cache_key_ip, 0) + 1
            cache.set(cache_key_ip, tentativas_ip, RateLimiter.LOCKOUT_TIME)
            
            logger.warning(
                f"Tentativa falhada: {identifier} - IP: {ip} - "
                f"Tentativas ID: {tentativas_id}/{RateLimiter.MAX_ATTEMPTS}, "
                f"Tentativas IP: {tentativas_ip}/{RateLimiter.MAX_ATTEMPTS}"
            )
        else:
            logger.warning(
                f"Tentativa falhada: {identifier} (sem IP) - "
                f"Tentativas: {tentativas_id}/{RateLimiter.MAX_ATTEMPTS}"
            )
    
    @staticmethod
    def reset_attempts(identifier, request=None):
        """
        Reseta o contador de tentativas após login bem-sucedido
        
        Args:
            identifier (str): Chave única
            request (HttpRequest): Objeto da requisição
        """
        # Resetar por identificador
        cache_key_id = f'rate_limit_id_{identifier}'
        cache.delete(cache_key_id)
        
        # ✅ Resetar por IP
        if request:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            cache_key_ip = f'rate_limit_ip_{ip}'
            cache.delete(cache_key_ip)
            
            logger.info(f"Login bem-sucedido: {identifier} - IP: {ip}")
        else:
            logger.info(f"Login bem-sucedido: {identifier} (sem IP)")


# ============================================================================
# VALIDADOR DE SENHA
# ============================================================================

class ValidadorSenha:
    """
    Validação de força de senha
    
    Configurações ajustáveis para balancear segurança e usabilidade
    """
    
    # ✅ Configurações mais razoáveis
    MIN_LENGTH = 8  # Mínimo 8 caracteres (antes era 12)
    REQUER_MAIUSCULA = True
    REQUER_MINUSCULA = True
    REQUER_NUMERO = True
    REQUER_ESPECIAL = False  # ✅ Opcional (não obrigatório)
    
    @staticmethod
    def validar(senha):
        """
        Valida a força da senha
        
        Args:
            senha (str): Senha a ser validada
        
        Returns:
            tuple: (válida: bool, mensagem: str)
        """
        if not senha:
            return False, "Senha não pode ser vazia"
        
        if len(senha) < ValidadorSenha.MIN_LENGTH:
            return False, f"Senha deve ter no mínimo {ValidadorSenha.MIN_LENGTH} caracteres"
        
        if ValidadorSenha.REQUER_MAIUSCULA and not re.search(r'[A-Z]', senha):
            return False, "Senha deve conter pelo menos uma letra maiúscula"
        
        if ValidadorSenha.REQUER_MINUSCULA and not re.search(r'[a-z]', senha):
            return False, "Senha deve conter pelo menos uma letra minúscula"
        
        if ValidadorSenha.REQUER_NUMERO and not re.search(r'[0-9]', senha):
            return False, "Senha deve conter pelo menos um número"
        
        if ValidadorSenha.REQUER_ESPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\\/]', senha):
            return False, "Senha deve conter pelo menos um caractere especial (!@#$%^&*)"
        
        return True, "Senha válida"
    
    @staticmethod
    def calcular_forca(senha):
        """
        Calcula a força da senha (0-100)
        
        Args:
            senha (str): Senha a ser avaliada
        
        Returns:
            int: Pontuação de força (0-100)
        """
        if not senha:
            return 0
        
        forca = 0
        
        # Comprimento (até 40 pontos)
        forca += min(len(senha) * 4, 40)
        
        # Variedade de caracteres
        if re.search(r'[a-z]', senha):
            forca += 10
        if re.search(r'[A-Z]', senha):
            forca += 10
        if re.search(r'[0-9]', senha):
            forca += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>\-_=+\[\]\\\/]', senha):
            forca += 20
        
        # Penalidades
        # Sequências repetidas
        if re.search(r'(.)\1{2,}', senha):
            forca -= 10
        
        # Sequências óbvias (123, abc, etc)
        if any(seq in senha.lower() for seq in ['123', 'abc', 'qwerty', 'password']):
            forca -= 20
        
        return max(0, min(100, forca))


# ============================================================================
# VALIDADOR DE CNPJ
# ============================================================================

class ValidadorCNPJ:
    """
    Validação completa de CNPJ seguindo o algoritmo oficial
    """
    
    @staticmethod
    def validar(cnpj):
        """
        Valida CNPJ pelo algoritmo oficial da Receita Federal
        
        Args:
            cnpj (str): CNPJ com ou sem formatação
        
        Returns:
            bool: True se válido, False caso contrário
        
        Examples:
            >>> ValidadorCNPJ.validar('11.222.333/0001-81')
            True
            >>> ValidadorCNPJ.validar('11222333000181')
            True
            >>> ValidadorCNPJ.validar('00.000.000/0000-00')
            False
        """
        if not cnpj:
            return False
        
        # Remove caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj) != 14:
            return False
        
        # Evita CNPJs com todos os dígitos iguais (00000000000000, 11111111111111, etc)
        if cnpj == cnpj[0] * 14:
            return False
        
        # ✅ Cálculo CORRETO do primeiro dígito verificador
        multiplicadores_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * multiplicadores_1[i] for i in range(12))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        if int(cnpj[12]) != dv1:
            return False
        
        # ✅ Cálculo CORRETO do segundo dígito verificador
        multiplicadores_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(cnpj[i]) * multiplicadores_2[i] for i in range(13))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        return int(cnpj[13]) == dv2
    
    @staticmethod
    def formatar(cnpj):
        """
        Formata CNPJ: 00.000.000/0000-00
        
        Args:
            cnpj (str): CNPJ sem formatação
        
        Returns:
            str: CNPJ formatado ou string original se inválido
        """
        if not cnpj:
            return cnpj
        
        # Remove caracteres não numéricos
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        
        # Formata se tiver 14 dígitos
        if len(cnpj_numeros) == 14:
            return (
                f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}."
                f"{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"
            )
        
        return cnpj


# ============================================================================
# VALIDADOR DE CPF
# ============================================================================

class ValidadorCPF:
    """
    Validação completa de CPF seguindo o algoritmo oficial
    """
    
    @staticmethod
    def validar(cpf):
        """
        Valida CPF pelo algoritmo oficial
        
        Args:
            cpf (str): CPF com ou sem formatação
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not cpf:
            return False
        
        # Remove caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verifica se tem 11 dígitos
        if len(cpf) != 11:
            return False
        
        # Evita CPFs com todos os dígitos iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcula primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        
        if int(cpf[9]) != dv1:
            return False
        
        # Calcula segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        
        return int(cpf[10]) == dv2
    
    @staticmethod
    def formatar(cpf):
        """
        Formata CPF: 000.000.000-00
        
        Args:
            cpf (str): CPF sem formatação
        
        Returns:
            str: CPF formatado ou string original se inválido
        """
        if not cpf:
            return cpf
        
        # Remove caracteres não numéricos
        cpf_numeros = re.sub(r'\D', '', cpf)
        
        # Formata se tiver 11 dígitos
        if len(cpf_numeros) == 11:
            return (
                f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}."
                f"{cpf_numeros[6:9]}-{cpf_numeros[9:]}"
            )
        
        return cpf


# ============================================================================
# DECORATOR DE AUTENTICAÇÃO
# ============================================================================

def requer_login(view_func):
    """
    Decorator para proteger views que requerem autenticação
    
    NOTA: Este decorator é um alias para AuthService.requer_login
    Mantido aqui por compatibilidade, mas recomenda-se usar
    diretamente AuthService.requer_login
    
    Usage:
        from app_controle.utils.security import requer_login
        
        @requer_login
        def minha_view(request):
            ...
    """
    from functools import wraps
    from django.shortcuts import redirect
    from ..services.auth_services import AuthService
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        loja = AuthService.loja_logada(request)
        if not loja:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            logger.warning(
                f"Tentativa de acesso sem autenticação - "
                f"IP: {ip} - Path: {request.path}"
            )
            messages.warning(
                request, 
                "Você precisa estar logado para acessar esta página."
            )
            return redirect('login')
        return view_func(request, *args, **kwargs)
    
    return wrapper