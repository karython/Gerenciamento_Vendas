# app_controle/services/auth_services.py
"""
Service de autenticação e gerenciamento de lojas
"""

from django.db import transaction
from functools import wraps
from django.shortcuts import redirect
from ..models import Loja
from ..utils.security import RateLimiter
import re


class AuthService:
    
    @staticmethod
    def validar_cnpj(cnpj):
        """
        Valida formato básico do CNPJ
        
        Returns:
            bool: True se válido, False caso contrário
        """
        # Remove caracteres não numéricos
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj_numeros) != 14:
            return False
        
        # Validação completa de CNPJ (dígitos verificadores)
        # TODO: Implementar validação completa se necessário
        return True
    
    @staticmethod
    def formatar_cnpj(cnpj):
        """
        Formata CNPJ: 00.000.000/0000-00
        
        Args:
            cnpj (str): CNPJ com ou sem formatação
            
        Returns:
            str: CNPJ formatado
        """
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        if len(cnpj_numeros) == 14:
            return (
                f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}."
                f"{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"
            )
        return cnpj
    
    @staticmethod
    @transaction.atomic
    def cadastrar_loja(dados):
        """
        Cadastra uma nova loja
        
        Args:
            dados (dict): Dados da loja
                - nome (str): Nome da loja
                - cnpj (str): CNPJ
                - senha (str): Senha em texto plano
                - telefone (str, opcional): Telefone
                - email (str, opcional): Email
                - endereco (str, opcional): Endereço
        
        Returns:
            Loja: Objeto da loja criada
        
        Raises:
            ValueError: Se dados inválidos ou CNPJ já cadastrado
        """
        # Validar dados obrigatórios
        if not dados.get('nome'):
            raise ValueError("Nome da loja é obrigatório")
        
        if not dados.get('cnpj'):
            raise ValueError("CNPJ é obrigatório")
        
        if not dados.get('senha'):
            raise ValueError("Senha é obrigatória")
        
        # Validar CNPJ
        cnpj = dados['cnpj']
        if not AuthService.validar_cnpj(cnpj):
            raise ValueError("CNPJ inválido. Deve conter 14 dígitos")
        
        # Formatar CNPJ
        cnpj_formatado = AuthService.formatar_cnpj(cnpj)
        
        # ✅ Verificar se CNPJ já existe
        if Loja.objects.filter(cnpj=cnpj_formatado).exists():
            raise ValueError("CNPJ já cadastrado no sistema")
        
        # Validar senha (será validada pelo Form também)
        if len(dados['senha']) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        
        # Criar loja
        loja = Loja(
            nome=dados['nome'],
            cnpj=cnpj_formatado,
            telefone=dados.get('telefone', ''),
            email=dados.get('email', ''),
            endereco=dados.get('endereco', '')
        )
        
        # A senha será hash automático pelo método set_password
        loja.set_password(dados['senha'])
        loja.save()
        
        return loja
    
    @staticmethod
    def autenticar_loja(cnpj, senha, request):
        """
        Autentica uma loja pelo CNPJ e senha
        OTIMIZADO: Busca apenas campos necessários + rate limiting
        
        Args:
            cnpj (str): CNPJ da loja (com ou sem formatação)
            senha (str): Senha em texto plano
            request (HttpRequest): Request para rate limiting
        
        Returns:
            tuple: (Loja ou None, mensagem_erro ou None)
        """
        # Formatar CNPJ
        cnpj_formatado = AuthService.formatar_cnpj(cnpj)
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        # ✅ Verificar rate limit ANTES de buscar no banco
        permitido, tentativas_restantes = RateLimiter.check_rate_limit(
            cnpj_formatado, 
            request
        )
        
        if not permitido:
            mensagem = (
                "❌ Muitas tentativas de login falhadas. "
                "Tente novamente em 15 minutos."
            )
            return (None, mensagem)
        
        try:
            # ✅ OTIMIZAÇÃO: Buscar APENAS campos necessários (novos nomes)
            loja = Loja.objects.only(
                'id', 'nome', 'cnpj', 'senha', 'ativo'  # ✅ Novos nomes
            ).get(cnpj=cnpj_formatado, ativo=True)  # ✅ Novos nomes
            
            # Verificar senha
            if loja.check_password(senha):
                # ✅ Login bem-sucedido - resetar tentativas
                RateLimiter.reset_attempts(cnpj_formatado, request)
                return (loja, None)
            else:
                # ❌ Senha incorreta - incrementar tentativas
                RateLimiter.increment_attempts(cnpj_formatado, request)
                _, tentativas_restantes = RateLimiter.check_rate_limit(
                    cnpj_formatado, 
                    request
                )
                
                if tentativas_restantes == 0:
                    mensagem = (
                        "❌ Muitas tentativas falhadas. "
                        "Tente novamente em 15 minutos."
                    )
                else:
                    mensagem = (
                        f"❌ CNPJ ou senha incorretos! "
                        f"({tentativas_restantes} tentativas restantes)"
                    )
                
                return (None, mensagem)
                
        except Loja.DoesNotExist:
            # ❌ CNPJ não encontrado - incrementar tentativas
            RateLimiter.increment_attempts(cnpj_formatado, request)
            _, tentativas_restantes = RateLimiter.check_rate_limit(
                cnpj_formatado, 
                request
            )
            
            if tentativas_restantes == 0:
                mensagem = (
                    "❌ Muitas tentativas falhadas. "
                    "Tente novamente em 15 minutos."
                )
            else:
                mensagem = (
                    f"❌ CNPJ ou senha incorretos! "
                    f"({tentativas_restantes} tentativas restantes)"
                )
            
            return (None, mensagem)
    
    @staticmethod
    def loja_logada(request):
        """
        Retorna a loja logada na sessão ou None
        OTIMIZADO: Busca apenas campos essenciais
        
        Args:
            request (HttpRequest): Request da requisição
            
        Returns:
            Loja ou None: Loja logada ou None se não houver
        """
        loja_id = request.session.get('loja_id')
        if loja_id:
            try:
                # ✅ Usar novos nomes de campos
                return Loja.objects.only(
                    'id', 'nome', 'cnpj', 'ativo'  # ✅ Novos nomes
                ).get(id=loja_id, ativo=True)  # ✅ Novos nomes
            except Loja.DoesNotExist:
                return None
        return None
    
    @staticmethod
    def fazer_login(request, loja):
        """
        Salva a loja na sessão
        
        Args:
            request (HttpRequest): Request da requisição
            loja (Loja): Objeto da loja autenticada
        """
        # ✅ Usar novos nomes de campos
        request.session['loja_id'] = loja.id  # ✅ Novo nome
        request.session['loja_nome'] = loja.nome  # ✅ Novo nome
        request.session['loja_cnpj'] = loja.cnpj  # ✅ Novo nome
    
    @staticmethod
    def fazer_logout(request):
        """
        Remove a loja da sessão
        
        Args:
            request (HttpRequest): Request da requisição
        """
        if 'loja_id' in request.session:
            del request.session['loja_id']
            del request.session['loja_nome']
            del request.session['loja_cnpj']
    
    @staticmethod
    def requer_login(view_func):
        """
        Decorator para proteger views que requerem login
        
        Usage:
            @AuthService.requer_login
            def minha_view(request):
                ...
        """
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            loja = AuthService.loja_logada(request)
            if not loja:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        
        return wrapper