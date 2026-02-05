# app_controle/views/auth_views.py

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from ..services.auth_services import AuthService
from ..utils.security import RateLimiter, ValidadorSenha, ValidadorCNPJ

logger = logging.getLogger('seguranca')

def index(request):
    """Página inicial - redireciona conforme estado de autenticação"""
    loja = AuthService.loja_logada(request)
    
    if loja:
        # Se já estiver logado, vai para o dashboard
        return redirect('dashboard')
    else:
        # Se não estiver logado, mostra página de boas-vindas
        return render(request, 'auth/index.html')

def cadastro(request):
    """Página de cadastro de nova loja"""
    # Se já estiver logado, redireciona
    if AuthService.loja_logada(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            dados = {
                'nome_loja': request.POST.get('nome_loja'),
                'cnpj': request.POST.get('cnpj'),
                'senha': request.POST.get('senha'),
                'senha_confirmacao': request.POST.get('senha_confirmacao'),
                'telefone': request.POST.get('telefone', ''),
                'email': request.POST.get('email', ''),
                'endereco': request.POST.get('endereco', ''),
            }
            
            # Validar confirmação de senha
            if dados['senha'] != dados['senha_confirmacao']:
                messages.error(request, '❌ As senhas não coincidem!')
                return render(request, 'auth/cadastro.html', {'dados': dados})
            
            # Validar força da senha
            senha_valida, mensagem_senha = ValidadorSenha.validar(dados['senha'])
            if not senha_valida:
                messages.error(request, f"❌ {mensagem_senha}")
                return render(request, 'auth/cadastro.html', {'dados': dados})
            
            # Validar CNPJ completamente
            if not ValidadorCNPJ.validar(dados['cnpj']):
                messages.error(request, '❌ CNPJ inválido!')
                logger.warning(f"Tentativa de cadastro com CNPJ inválido: {dados['cnpj']} - IP: {request.META.get('REMOTE_ADDR')}")
                return render(request, 'auth/cadastro.html', {'dados': dados})
            
            # Cadastrar loja (SEM fazer login automático)
            loja = AuthService.cadastrar_loja(dados)
            
            # Redirecionar para página de login com mensagem de sucesso
            logger.info(f"Nova loja cadastrada: {loja.NOME_LOJA} - IP: {request.META.get('REMOTE_ADDR')}")
            messages.success(request, f'✅ Loja {loja.NOME_LOJA} cadastrada com sucesso! Faça login para continuar.')
            return redirect('login')
            
        except ValueError as e:
            messages.error(request, f'❌ {str(e)}')
            logger.warning(f"Erro no cadastro: {str(e)} - IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'auth/cadastro.html', {'dados': dados})
        except Exception as e:
            print(f"[ERRO CADASTRO] {e}")
            messages.error(request, '❌ Erro ao cadastrar loja. Tente novamente.')
            logger.error(f"Erro inesperado no cadastro: {str(e)} - IP: {request.META.get('REMOTE_ADDR')}")
            return render(request, 'auth/cadastro.html', {'dados': dados})
    
    return render(request, 'auth/cadastro.html')

def login(request):
    """Página de login com proteção contra brute force"""
    # Se já estiver logado, redireciona
    if AuthService.loja_logada(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj', '').strip()
        senha = request.POST.get('senha', '').strip()
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        if not cnpj or not senha:
            messages.error(request, '❌ Preencha CNPJ e senha!')
            logger.warning(f"Tentativa de login com campos vazios - IP: {ip}")
            return render(request, 'auth/login.html', {'cnpj': cnpj})
        
        # ============================================
        # VERIFICAR RATE LIMIT (Proteção contra brute force)
        # ============================================
        permitido, tentativas = RateLimiter.check_rate_limit(cnpj, request)
        
        if not permitido:
            mensagem = (
                f"❌ Muitas tentativas de login falhadas. "
                f"Tente novamente em 15 minutos."
            )
            messages.error(request, mensagem)
            logger.warning(f"Rate limit atingido para CNPJ: {cnpj} - IP: {ip}")
            return render(request, 'auth/login.html', {'cnpj': cnpj})
        
        # Autenticar (verifica no banco de dados)
        loja = AuthService.autenticar_loja(cnpj, senha)
        
        if loja:
            # Login bem-sucedido - loja existe no banco e senha está correta
            AuthService.fazer_login(request, loja)
            RateLimiter.reset_attempts(cnpj, request)  # Limpar tentativas
            
            logger.info(f"Login bem-sucedido: {loja.NOME_LOJA} (CNPJ: {loja.CNPJ}) - IP: {ip}")
            return redirect('nova_venda')
        else:
            # Credenciais inválidas
            RateLimiter.increment_attempts(cnpj, request)  # Incrementar tentativas
            
            _, tentativas_restantes = RateLimiter.check_rate_limit(cnpj, request)
            
            if tentativas_restantes == 0:
                mensagem = "❌ Muitas tentativas falhadas. Tente novamente em 15 minutos."
            else:
                mensagem = f"❌ CNPJ ou senha incorretos! ({tentativas_restantes} tentativas restantes)"
            
            messages.error(request, mensagem)
            logger.warning(f"Falha de login: CNPJ {cnpj} - IP: {ip}")
            return render(request, 'auth/login.html', {'cnpj': cnpj})
    
    return render(request, 'auth/login.html')

def logout(request):
    """Fazer logout"""
    AuthService.fazer_logout(request)
    # Limpar todas as mensagens pendentes
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    storage.used = True
    # Limpar completamente a sessão
    request.session.flush()
    
    return redirect('login')