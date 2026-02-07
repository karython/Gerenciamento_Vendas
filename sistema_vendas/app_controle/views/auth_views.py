# app_controle/views/auth_views.py
"""
Views de autenticação: login, cadastro e logout
"""

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from ..services.auth_services import AuthService
from ..forms import LojaRegistrationForm, LojaLoginForm

logger = logging.getLogger('seguranca')


def index(request):
    """
    Página inicial - redireciona para dashboard se autenticado, senão para login
    """
    if AuthService.loja_logada(request):
        return redirect('dashboard')
    return redirect('login')


def cadastro(request):
    """Página de cadastro de nova loja"""
    if AuthService.loja_logada(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LojaRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                loja = AuthService.cadastrar_loja(form.cleaned_data)
                
                logger.info(
                    f"Nova loja cadastrada: {loja.nome} - "
                    f"IP: {request.META.get('REMOTE_ADDR')}"
                )
                
                messages.success(
                    request,
                    f'✅ Loja {loja.nome} cadastrada com sucesso! '
                    'Faça login para continuar.'
                )
                return redirect('login')
                
            except ValueError as e:
                messages.error(request, f'❌ {str(e)}')
            except Exception as e:
                messages.error(request, '❌ Erro ao cadastrar loja.')
                logger.error(f"Erro no cadastro: {str(e)}", exc_info=True)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'❌ {error}')
    else:
        form = LojaRegistrationForm()
    
    return render(request, 'auth/cadastro.html', {'form': form})


def login(request):
    """Página de login com proteção contra brute force"""
    if AuthService.loja_logada(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LojaLoginForm(request.POST)
        
        if form.is_valid():
            cnpj = form.cleaned_data['cnpj']
            senha = form.cleaned_data['senha']
            
            loja, mensagem_erro = AuthService.autenticar_loja(cnpj, senha, request)
            
            if loja:
                AuthService.fazer_login(request, loja)
                return redirect('dashboard')
            else:
                messages.error(request, mensagem_erro)
        else:
            messages.error(request, '❌ Preencha CNPJ e senha corretamente!')
    else:
        form = LojaLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def logout(request):
    """Logout do sistema"""
    loja_nome = request.session.get('loja_nome', 'Desconhecida')
    
    # Fazer logout via service
    AuthService.fazer_logout(request)
    
    logger.info(
        f"Logout realizado: Loja '{loja_nome}' - "
        f"IP: {request.META.get('REMOTE_ADDR')}"
    )
    
    messages.success(request, '✅ Logout realizado com sucesso!')
    return redirect('login')


