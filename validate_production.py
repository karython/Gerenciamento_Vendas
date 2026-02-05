#!/usr/bin/env python
"""
Script de Validação de Configurações de Segurança
Executa várias verificações antes de colocar em produção
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório sistema_vendas ao path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sistema_vendas'))

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check(condition, message_success, message_error):
    """Verifica uma condição e imprime resultado"""
    if condition:
        print(f"{Colors.GREEN}✓{Colors.END} {message_success}")
        return True
    else:
        print(f"{Colors.RED}✗{Colors.END} {message_error}")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}VALIDAÇÃO DE CONFIGURAÇÕES DE PRODUÇÃO{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    checks_passed = 0
    checks_total = 0
    
    # ============================================
    # 1. Verificar arquivo .env
    # ============================================
    print(f"{Colors.BLUE}[1] Verificando arquivo .env{Colors.END}")
    checks_total += 1
    
    env_path = Path('.env')
    if check(env_path.exists(), 
             "Arquivo .env encontrado",
             "❌ Arquivo .env não encontrado!"):
        checks_passed += 1
    
    # ============================================
    # 2. Verificar variáveis de ambiente críticas
    # ============================================
    print(f"\n{Colors.BLUE}[2] Verificando variáveis de ambiente críticas{Colors.END}")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'SECRET_KEY': 'Chave secreta do Django',
        'DEBUG': 'Flag de debug',
        'DB_NAME': 'Nome do banco de dados',
        'DB_USER': 'Usuário do banco',
        'DB_PASSWORD': 'Senha do banco',
        'DB_HOST': 'Host do banco',
        'ALLOWED_HOSTS': 'Hosts permitidos',
    }
    
    for var, description in required_vars.items():
        checks_total += 1
        value = os.getenv(var)
        if check(value, 
                f"{description} ({var}) configurado",
                f"❌ {description} ({var}) não configurado!"):
            checks_passed += 1
            # Alertar se SECRET_KEY ainda é insegura
            if var == 'SECRET_KEY' and value and 'insecure' in value:
                print(f"{Colors.YELLOW}⚠{Colors.END}  SECRET_KEY parece insegura (contém 'insecure')")
    
    # ============================================
    # 3. Verificar configurações do Django
    # ============================================
    print(f"\n{Colors.BLUE}[3] Verificando configurações do Django{Colors.END}")
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_vendas.settings')
    
    try:
        import django
        django.setup()
        from django.conf import settings
        
        # DEBUG deve ser False
        checks_total += 1
        if check(not settings.DEBUG,
                 "DEBUG está desabilitado (False)",
                 f"❌ DEBUG está habilitado! DEBUG={settings.DEBUG}"):
            checks_passed += 1
        else:
            print(f"{Colors.YELLOW}⚠{Colors.END}  DEBUG deve ser False em produção!")
        
        # ALLOWED_HOSTS não deve estar vazio
        checks_total += 1
        if check(settings.ALLOWED_HOSTS and len(settings.ALLOWED_HOSTS) > 0,
                 f"ALLOWED_HOSTS configurado: {settings.ALLOWED_HOSTS}",
                 "❌ ALLOWED_HOSTS está vazio!"):
            checks_passed += 1
        
        # SESSION_COOKIE_HTTPONLY deve ser True
        checks_total += 1
        if check(settings.SESSION_COOKIE_HTTPONLY,
                 "SESSION_COOKIE_HTTPONLY está habilitado",
                 "❌ SESSION_COOKIE_HTTPONLY deve ser True!"):
            checks_passed += 1
        
        # Em produção, cookies devem ser seguros
        if not settings.DEBUG:
            checks_total += 1
            if check(settings.SESSION_COOKIE_SECURE,
                    "SESSION_COOKIE_SECURE habilitado (produção)",
                    "❌ SESSION_COOKIE_SECURE deve ser True em produção!"):
                checks_passed += 1
        
        # CSRF Middleware
        checks_total += 1
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware'
        if check(csrf_middleware in settings.MIDDLEWARE,
                 "Proteção CSRF habilitada",
                 "❌ Middleware CSRF não está habilitado!"):
            checks_passed += 1
        
        # XFrame Options
        checks_total += 1
        if check(hasattr(settings, 'X_FRAME_OPTIONS') and settings.X_FRAME_OPTIONS == 'DENY',
                 "Proteção contra clickjacking habilitada",
                 "❌ X_FRAME_OPTIONS não está configurado para DENY!"):
            checks_passed += 1
        
    except Exception as e:
        print(f"{Colors.RED}✗ Erro ao verificar Django:{Colors.END} {e}")
        return 1
    
    # ============================================
    # 4. Verificar dependências
    # ============================================
    print(f"\n{Colors.BLUE}[4] Verificando dependências{Colors.END}")
    
    required_packages = {
        'django': 'Django',
        'MySQLdb': 'MySQL Client',
        'dotenv': 'Python Dotenv',
        'reportlab': 'ReportLab',
    }
    
    for package, name in required_packages.items():
        checks_total += 1
        try:
            __import__(package)
            if check(True,
                    f"{name} instalado",
                    f"{name} não encontrado"):
                checks_passed += 1
        except ImportError:
            checks_passed += 0
    
    # ============================================
    # 5. Verificar arquivo .gitignore
    # ============================================
    print(f"\n{Colors.BLUE}[5] Verificando segurança de arquivos sensíveis{Colors.END}")
    
    gitignore_path = Path('.gitignore')
    checks_total += 1
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
            if check('.env' in content,
                    ".env está no .gitignore",
                    "❌ .env não está no .gitignore!"):
                checks_passed += 1
    else:
        print(f"{Colors.YELLOW}⚠{Colors.END}  Arquivo .gitignore não encontrado")
    
    # ============================================
    # Resultado Final
    # ============================================
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"Resultado: {Colors.GREEN}{checks_passed}{Colors.END}/{checks_total} verificações passaram")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if checks_passed == checks_total:
        print(f"{Colors.GREEN}✓ Todas as configurações estão corretas!{Colors.END}")
        print(f"{Colors.GREEN}✓ Sistema pronto para produção!{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.YELLOW}⚠ Algumas configurações precisam ser ajustadas.{Colors.END}")
        print(f"{Colors.YELLOW}⚠ Não implante em produção até resolver os problemas acima.{Colors.END}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
