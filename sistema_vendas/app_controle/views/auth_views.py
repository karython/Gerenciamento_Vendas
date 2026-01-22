# app_controle/views/auth_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from ..services.auth_services import AuthService

def index(request):
    """Página inicial - redireciona conforme estado de autenticação"""
    loja = AuthService.loja_logada(request)
    
    if loja:
        # Se já estiver logado, vai para o dashboard
        return redirect('home')
    else:
        # Se não estiver logado, mostra página de boas-vindas
        return render(request, 'auth/index.html')

def cadastro(request):
    """Página de cadastro de nova loja"""
    # Se já estiver logado, redireciona
    if AuthService.loja_logada(request):
        return redirect('home')
    
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
            
            # Cadastrar loja (SEM fazer login automático)
            loja = AuthService.cadastrar_loja(dados)
            
            # Redirecionar para página de login com mensagem de sucesso
            messages.success(request, f'✅ Loja {loja.NOME_LOJA} cadastrada com sucesso! Faça login para continuar.')
            return redirect('login')
            
        except ValueError as e:
            messages.error(request, f'❌ {str(e)}')
            return render(request, 'auth/cadastro.html', {'dados': dados})
        except Exception as e:
            print(f"[ERRO CADASTRO] {e}")
            messages.error(request, '❌ Erro ao cadastrar loja. Tente novamente.')
            return render(request, 'auth/cadastro.html', {'dados': dados})
    
    return render(request, 'auth/cadastro.html')

def login(request):
    """Página de login"""
    # Se já estiver logado, redireciona
    if AuthService.loja_logada(request):
        return redirect('home')
    
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        senha = request.POST.get('senha')
        
        if not cnpj or not senha:
            messages.error(request, '❌ Preencha CNPJ e senha!')
            return render(request, 'auth/login.html', {'cnpj': cnpj})
        
        # Autenticar (verifica no banco de dados)
        loja = AuthService.autenticar_loja(cnpj, senha)
        
        if loja:
            # Login bem-sucedido - loja existe no banco e senha está correta
            AuthService.fazer_login(request, loja)
            messages.success(request, f'✅ Bem-vindo(a), {loja.NOME_LOJA}!')
            return redirect('home')
        else:
            # Credenciais inválidas (CNPJ não existe ou senha incorreta)
            messages.error(request, '❌ CNPJ ou senha incorretos!')
            return render(request, 'auth/login.html', {'cnpj': cnpj})
    
    return render(request, 'auth/login.html')

def logout(request):
    """Fazer logout"""
    AuthService.fazer_logout(request)
    messages.success(request, '✅ Logout realizado com sucesso!')
    return redirect('index')