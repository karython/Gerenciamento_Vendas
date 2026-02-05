# 🔐 Análise de Segurança - Gerenciamento de Login

**Data da análise:** 5 de fevereiro de 2026  
**Projeto:** Sistema de Gerenciamento de Vendas  
**Escopo:** Autenticação, Sessões e Configurações de Segurança

---

## 📋 Resumo Executivo

O projeto utiliza um sistema de autenticação customizado baseado em **sessões Django**. Embora tenha implementações corretas em alguns aspectos, **existem vulnerabilidades críticas e medianas que precisam ser abordadas urgentemente**.

**Risco Geral:** 🔴 **ALTO** (Crítico)

---

## ✅ Pontos Positivos

### 1. **Hashing de Senha** (Correto)
```python
# auth_services.py - método autenticar_loja()
if loja.check_password(senha):
```
- Utiliza `check_password()` do Django, que usa **PBKDF2** por padrão
- Senhas não são armazenadas em texto plano
- ✅ **Status:** Implementado corretamente

### 2. **Proteção contra CSRF** (Habilitada)
```python
# settings.py
'django.middleware.csrf.CsrfViewMiddleware',
```
- Middleware CSRF está ativo
- Templates devem usar `{% csrf_token %}`
- ✅ **Status:** Configurado

### 3. **Sessão Segura (Parcialmente)**
```python
# settings.py
SESSION_COOKIE_HTTPONLY = True  # ✅ Previne XSS
SESSION_SAVE_EVERY_REQUEST = True  # ✅ Mantém sessão ativa
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # ✅ Expira ao fechar navegador
```
- HTTPOnly previne acesso via JavaScript (proteção XSS)
- Sessão renovada a cada requisição
- ✅ **Status:** Bem configurado

### 4. **Validação de CNPJ** (Implementado)
```python
# auth_services.py
if not AuthService.validar_cnpj(cnpj):
    raise ValueError("CNPJ inválido. Deve conter 14 dígitos")
```
- Valida formato básico de CNPJ
- ✅ **Status:** Implementado

### 5. **Decorator de Proteção** (Existe)
```python
# auth_services.py
@staticmethod
def requer_login(view_func):
    """Decorator para proteger views que requerem login"""
```
- Ferramenta disponível para proteger views
- ✅ **Status:** Código existe (mas ver seção de problemas)

### 6. **Middleware de Verificação de Loja Ativa**
```python
# middleware.py - SessionExpireMiddleware
# Verifica se loja ainda está ativa a cada requisição
```
- Invalida sessão se loja for desativada
- Usa cache para otimizar (evita queries desnecessárias)
- ✅ **Status:** Implementado e otimizado

---

## 🚨 PROBLEMAS CRÍTICOS

### 1. **🔴 SECRET_KEY EXPOSTA NO REPOSITÓRIO**
**Severidade:** CRÍTICA  
**Arquivo:** `settings.py`

```python
SECRET_KEY = 'django-insecure-3q-&=6squefv$e)ikci3&wk6tb4mi_%9)39t%bvbn@8=3f9i#x'
```

**Riscos:**
- Secret key é usada para criptografar tokens CSRF, cookies de sessão, etc.
- Se estiver no Git, qualquer pessoa pode:
  - Falsificar tokens CSRF
  - Sequestrar sessões
  - Descriptografar mensagens assinadas
  - Realizar session fixation attacks

**Ação Imediata Necessária:**
1. Gerar nova SECRET_KEY
2. Remover do Git (adicionar a .gitignore)
3. Usar variável de ambiente

**Solução:**
```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback')
```

### 2. **🔴 DEBUG = True EM TUDO**
**Severidade:** CRÍTICA  
**Arquivo:** `settings.py`

```python
DEBUG = True
```

**Riscos:**
- Expõe informações sensíveis em caso de erro (paths, variáveis de ambiente)
- Mostra stack traces detalhados
- Django carrega estaticamente assets (não é eficiente)
- Página de erro do Django revela a estrutura do projeto

**Ação:**
```python
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### 3. **🔴 ALLOWED_HOSTS VAZIO**
**Severidade:** ALTA  
**Arquivo:** `settings.py`

```python
ALLOWED_HOSTS = []
```

**Riscos:**
- Em produção, qualquer Host pode acessar a aplicação
- Vulnerável a ataques de Host Header Injection

**Ação:**
```python
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

### 4. **🔴 CREDENCIAIS DO BANCO DE DADOS EXPOSTAS**
**Severidade:** CRÍTICA  
**Arquivo:** `settings.py`

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'u275872813_gen_estoque',
        'USER': 'u275872813_admin_estoque',
        'PASSWORD': 'GestaoEstoque25',  # ❌ Senha em texto plano!
        'HOST': 'srv1061.hstgr.io',
    }
}
```

**Riscos:**
- Qualquer pessoa com acesso ao repositório tem credenciais do banco
- Acesso não autorizado ao banco de dados
- Violação de dados sensíveis

**Ação Imediata:**
1. **Mudar senha do banco de dados AGORA**
2. Usar .env ou variáveis de ambiente
3. Adicionar settings a .gitignore

---

## ⚠️ PROBLEMAS MEDIANOS (Importantes)

### 5. **⚠️ Decorator `@requer_login` NÃO ESTÁ SENDO USADO**
**Severidade:** ALTA  
**Arquivo:** Views

```python
# auth_services.py - O decorator existe
@staticmethod
def requer_login(view_func):
    """Decorator para proteger views"""
    ...

# Mas verificando auth_views.py, este decorator NÃO é usado!
# Em vez disso, cada view faz verificação manual:
def index(request):
    loja = AuthService.loja_logada(request)
    if loja:
        return redirect('dashboard')
```

**Problema:**
- Múltiplas views podem ter sido esquecidas de proteção
- Falta padrão consistente

**Ação:**
```python
# Aplicar em TODAS as views que requerem login
from app_controle.services.auth_services import AuthService

@AuthService.requer_login
def dashboard(request):
    loja = AuthService.loja_logada(request)
    ...
```

### 6. **⚠️ Senha Mínima Muito Fraca**
**Severidade:** MÉDIA  
**Arquivo:** `auth_services.py`

```python
if len(dados['senha']) < 6:
    raise ValueError("Senha deve ter no mínimo 6 caracteres")
```

**Problema:**
- Apenas 6 caracteres é muito fraco
- Sem requisitos de complexidade (maiúsculas, números, símbolos)
- Vulnerável a ataques de força bruta

**Recomendação:**
```python
if len(dados['senha']) < 12:
    raise ValueError("Senha deve ter no mínimo 12 caracteres")

# Adicionar validação de complexidade
import re
def validar_forca_senha(senha):
    """Valida força da senha"""
    if len(senha) < 12:
        return False, "Mínimo 12 caracteres"
    if not re.search(r'[A-Z]', senha):
        return False, "Deve conter letra maiúscula"
    if not re.search(r'[a-z]', senha):
        return False, "Deve conter letra minúscula"
    if not re.search(r'[0-9]', senha):
        return False, "Deve conter número"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return False, "Deve conter caractere especial"
    return True, "Senha forte"
```

### 7. **⚠️ Falta de Rate Limiting (Brute Force)**
**Severidade:** ALTA  
**Problema:** Nenhuma proteção contra tentativas repetidas de login

```python
# auth_views.py - login view
def login(request):
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        senha = request.POST.get('senha')
        # ❌ Nenhuma verificação de tentativas falhas!
        loja = AuthService.autenticar_loja(cnpj, senha)
```

**Risco:**
- Atacante pode testar senhas infinitamente
- Força bruta não é detectada

**Ação:**
```python
from django.core.cache import cache

def login(request):
    if request.method == 'POST':
        cnpj = request.POST.get('cnpj')
        senha = request.POST.get('senha')
        
        # Verificar tentativas de login
        cache_key = f'login_attempts_{cnpj}'
        tentativas = cache.get(cache_key, 0)
        
        if tentativas >= 5:
            messages.error(request, 'Muitas tentativas. Tente novamente em 15 minutos.')
            return render(request, 'auth/login.html')
        
        loja = AuthService.autenticar_loja(cnpj, senha)
        
        if not loja:
            cache.set(cache_key, tentativas + 1, 60 * 15)  # 15 minutos
            messages.error(request, 'CNPJ ou senha incorretos!')
            return render(request, 'auth/login.html')
        
        cache.delete(cache_key)  # Limpar tentativas no sucesso
        AuthService.fazer_login(request, loja)
        return redirect('dashboard')
```

### 8. **⚠️ Falta de HTTPS Forçado**
**Severidade:** ALTA  
**Arquivo:** `settings.py`

```python
# Não há configurações de HTTPS
# SESSION_COOKIE_SECURE = True  # Comentado!
# CSRF_COOKIE_SECURE = True     # Não existe
# SECURE_SSL_REDIRECT = True     # Não existe
```

**Problema:**
- Cookies e dados de sessão podem ser interceptados em HTTP
- Man-in-the-middle attack possível

**Ação (Produção):**
```python
# settings.py
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 9. **⚠️ Falta de Logging de Eventos de Segurança**
**Severidade:** MÉDIA  

```python
# auth_services.py - Usa print() para logging!
print("[AUTH SERVICE] ✅ Login bem-sucedido: {loja.NOME_LOJA}")
```

**Problema:**
- Print não é persistido
- Impossível fazer auditoria
- Ataques não são rastreados

**Ação:**
```python
import logging

logger = logging.getLogger('seguranca')

# Em vez de print:
logger.info(f"Login bem-sucedido: {loja.NOME_LOJA} - IP: {request.META.get('REMOTE_ADDR')}")
logger.warning(f"Falha de login: {cnpj} - IP: {request.META.get('REMOTE_ADDR')}")
logger.error(f"Tentativa suspeita de acesso: {request.path} - IP: {request.META.get('REMOTE_ADDR')}")
```

### 10. **⚠️ Modelo Usuario Não Está Sendo Usado**
**Severidade:** MÉDIA  
**Arquivo:** `models/usuario.py`

```python
class Usuario(models.Model):
    idUSUARIO = models.AutoField(primary_key=True)
    NOME_USUARIO = models.CharField(max_length=120)
    EMAIL = models.CharField(max_length=120)
    SENHA = models.CharField(max_length=255)
```

**Problemas:**
- Esse modelo não é usado (autenticação usa `Loja`)
- Senha está em CharField (precisa usar password field)
- Email não é único
- Sem timestamps

---

## 📋 Outras Observações

### 11. Falta de Proteção contra Clickjacking (Parcial)
✅ X-Frame-Options está configurado:
```python
'django.middleware.clickjacking.XFrameOptionsMiddleware',
```

### 12. Validação de CNPJ Incompleta
```python
# Apenas valida tamanho, não o algoritmo
# Deve ser:
def validar_cnpj_completo(cnpj):
    """Valida CNPJ pelo algoritmo de verificação"""
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        return False
    
    # Verificação 1
    soma = sum(int(cnpj[i]) * (5 - (i % 4)) for i in range(8))
    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[8]) != dv1:
        return False
    
    # Verificação 2
    soma = sum(int(cnpj[i]) * (6 - (i % 4)) for i in range(8, 12))
    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto
    
    return int(cnpj[9]) == dv2
```

---

## 🛠️ PLANO DE AÇÃO PRIORITIZADO

### **URGENTE** (Executar em 24h)
- [ ] Gerar nova SECRET_KEY e remover do repositório
- [ ] Mudar senha do banco de dados
- [ ] Adicionar arquivo `.env` com variáveis sensíveis
- [ ] Adicionar `.env` e `settings_prod.py` ao `.gitignore`
- [ ] Configurar variáveis de ambiente

### **ALTA PRIORIDADE** (Esta semana)
- [ ] Implementar rate limiting para login
- [ ] Usar decorator `@requer_login` em todas as views protegidas
- [ ] Adicionar logging de segurança
- [ ] Aumentar requisito de força de senha para 12 caracteres
- [ ] Validação completa de CNPJ (algoritmo)
- [ ] Configurar HTTPS em produção

### **MÉDIA PRIORIDADE** (Próximas 2 semanas)
- [ ] Implementar autenticação com 2FA (opcional, mas recomendado)
- [ ] Adicionar recuperação de senha segura (email token)
- [ ] Revisar todas as views para proteção de acesso
- [ ] Implementar audit log de ações críticas
- [ ] Testes de segurança automatizados

### **MELHORIAS FUTURAS**
- [ ] Implementar OAuth2 / OpenID Connect
- [ ] Adicionar detecção de anomalias
- [ ] Security headers (CSP, X-Content-Type-Options, etc.)

---

## 📝 Checklist para Produção

```
ANTES DE COLOCAR EM PRODUÇÃO:
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS configurado
- [ ] SECRET_KEY segura e em variável de ambiente
- [ ] Banco de dados com credenciais em .env
- [ ] HTTPS habilitado
- [ ] SESSION_COOKIE_SECURE = True
- [ ] CSRF_COOKIE_SECURE = True
- [ ] Rate limiting implementado
- [ ] Logging de segurança configurado
- [ ] Validação forte de senhas
- [ ] Decorator @requer_login em todas as views protegidas
- [ ] Testes de segurança executados
```

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security Guide](https://docs.djangoproject.com/en/5.2/topics/security/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

---

**Análise realizada por:** GitHub Copilot  
**Data:** 5 de fevereiro de 2026
