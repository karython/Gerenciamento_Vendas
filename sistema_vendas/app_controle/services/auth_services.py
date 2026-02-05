# app_controle/services/auth_service.py

from django.db import transaction
from ..models import Loja
import re

class AuthService:
    
    @staticmethod
    def validar_cnpj(cnpj):
        """Valida formato do CNPJ"""
        # Remove caracteres não numéricos
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        
        # Verifica se tem 14 dígitos
        if len(cnpj_numeros) != 14:
            return False
        
        # Aqui você pode adicionar validação mais completa do CNPJ
        # Por enquanto, apenas verifica o tamanho
        return True
    
    @staticmethod
    def formatar_cnpj(cnpj):
        """Formata CNPJ: 00.000.000/0000-00"""
        cnpj_numeros = re.sub(r'\D', '', cnpj)
        if len(cnpj_numeros) == 14:
            return f"{cnpj_numeros[:2]}.{cnpj_numeros[2:5]}.{cnpj_numeros[5:8]}/{cnpj_numeros[8:12]}-{cnpj_numeros[12:]}"
        return cnpj
    
    @staticmethod
    @transaction.atomic
    def cadastrar_loja(dados):
        """
        Cadastra uma nova loja
        
        Args:
            dados: dict com nome_loja, cnpj, senha, telefone (opcional), email (opcional)
        
        Returns:
            Loja: objeto da loja criada
        
        Raises:
            ValueError: se dados inválidos ou CNPJ já cadastrado
        """
        print("=" * 50)
        print("[AUTH SERVICE] Cadastrando nova loja...")
        
        # Validar dados obrigatórios
        if not dados.get('nome_loja'):
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
        
        # Verificar se CNPJ já existe
        if Loja.objects.filter(CNPJ=cnpj_formatado).exists():
            raise ValueError("CNPJ já cadastrado no sistema")
        
        # Validar senha (mínimo 6 caracteres)
        if len(dados['senha']) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")
        
        # Criar loja
        loja = Loja(
            NOME_LOJA=dados['nome_loja'],
            CNPJ=cnpj_formatado,
            TELEFONE=dados.get('telefone', ''),
            EMAIL=dados.get('email', ''),
            ENDERECO=dados.get('endereco', '')
        )
        
        # A senha será criptografada automaticamente no save()
        loja.SENHA = dados['senha']
        loja.save()
        
        print(f"[AUTH SERVICE] ✅ Loja '{loja.NOME_LOJA}' cadastrada com sucesso!")
        print(f"[AUTH SERVICE]    CNPJ: {loja.CNPJ}")
        print(f"[AUTH SERVICE]    ID: {loja.idLOJA}")
        print("=" * 50)
        
        return loja
    
    @staticmethod
    def autenticar_loja(cnpj, senha):
        """
        Autentica uma loja pelo CNPJ e senha
        OTIMIZADO: Busca apenas campos necessários para validação
        
        Args:
            cnpj: CNPJ da loja (com ou sem formatação)
            senha: Senha em texto plano
        
        Returns:
            Loja: objeto da loja se autenticado
            None: se credenciais inválidas
        """
        print("=" * 50)
        print("[AUTH SERVICE] Tentando autenticar loja...")
        
        # Formatar CNPJ
        cnpj_formatado = AuthService.formatar_cnpj(cnpj)
        print(f"[AUTH SERVICE] CNPJ: {cnpj_formatado}")
        
        try:
            # OTIMIZAÇÃO: Buscar APENAS os campos necessários para validação
            # Isso reduz o tamanho da query e a transferência de dados
            loja = Loja.objects.only(
                'idLOJA', 'NOME_LOJA', 'CNPJ', 'SENHA', 'ATIVO'
            ).get(CNPJ=cnpj_formatado, ATIVO=True)
            
            # Verificar senha
            if loja.check_password(senha):
                print(f"[AUTH SERVICE] ✅ Login bem-sucedido: {loja.NOME_LOJA}")
                print("=" * 50)
                return loja
            else:
                print("[AUTH SERVICE] ❌ Senha incorreta")
                print("=" * 50)
                return None
                
        except Loja.DoesNotExist:
            print("[AUTH SERVICE] ❌ CNPJ não encontrado ou loja inativa")
            print("=" * 50)
            return None
    
    @staticmethod
    def loja_logada(request):
        """
        Retorna a loja logada na sessão ou None
        OTIMIZADO: Busca apenas campos essenciais
        """
        loja_id = request.session.get('loja_id')
        if loja_id:
            try:
                return Loja.objects.only(
                    'idLOJA', 'NOME_LOJA', 'CNPJ', 'ATIVO'
                ).get(idLOJA=loja_id, ATIVO=True)
            except Loja.DoesNotExist:
                return None
        return None
    
    @staticmethod
    def fazer_login(request, loja):
        """Salva a loja na sessão"""
        request.session['loja_id'] = loja.idLOJA
        request.session['loja_nome'] = loja.NOME_LOJA
        request.session['loja_cnpj'] = loja.CNPJ
        print(f"[AUTH SERVICE] Loja {loja.NOME_LOJA} salva na sessão")
    
    @staticmethod
    def fazer_logout(request):
        """Remove a loja da sessão"""
        if 'loja_id' in request.session:
            loja_nome = request.session.get('loja_nome')
            del request.session['loja_id']
            del request.session['loja_nome']
            del request.session['loja_cnpj']
            print(f"[AUTH SERVICE] Logout da loja {loja_nome}")
    
    @staticmethod
    def requer_login(view_func):
        """Decorator para proteger views que requerem login"""
        from functools import wraps
        from django.shortcuts import redirect
        
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            loja = AuthService.loja_logada(request)
            if not loja:
                print("[AUTH SERVICE] ⚠️ Tentativa de acesso sem login - redirecionando...")
                return redirect('login')
            return view_func(request, *args, **kwargs)
        
        return wrapper