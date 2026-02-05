# ⚡ Quick Start - Preparando para Produção

## 🚨 Ações Imediatas (Antes de fazer deploy!)

### 1️⃣ Gerar Nova SECRET_KEY
```bash
cd sistema_vendas
python manage.py shell
```

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
# Copie o resultado para .env (SECRET_KEY=...)
exit()
```

### 2️⃣ Configurar arquivo .env
```bash
cp .env.example .env
nano .env  # ou seu editor preferido
```

**Preencha as seguintes variáveis:**

```env
# Copiada do passo 1
SECRET_KEY=<sua-chave-gerada-aqui>

# Desabilitar debug em produção
DEBUG=False

# Seus domínios
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# Banco de dados (MUDAR URGENTEMENTE!)
DB_ENGINE=django.db.backends.mysql
DB_NAME=seu_banco_novo
DB_USER=novo_usuario_bd
DB_PASSWORD=SENHA_SUPER_SEGURA_NOVA
DB_HOST=seu-host-bd.com
DB_PORT=3306

# HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 3️⃣ Instalar Dependências
```bash
pip install python-dotenv
# ou
pip install -r requirements.txt
```

### 4️⃣ Validar Configuração
```bash
python3 validate_production.py
```

Você deve ver: `✓ Todas as configurações estão corretas!`

### 5️⃣ Testar em Desenvolvimento
```bash
# Com as novas configurações
python manage.py runserver
```

## 📋 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `.env` | Configurações sensíveis (⚠️ NUNCA commitar!) |
| `PRODUCAO.md` | Guia completo de deployment |
| `CORRECOES_IMPLEMENTADAS.md` | Resumo das mudanças |
| `ANALISE_SEGURANCA_LOGIN.md` | Relatório de segurança |
| `validate_production.py` | Script de validação |

## 🔒 Segurança

### O que foi corrigido:
- ✅ SECRET_KEY segura
- ✅ DEBUG desabilitado
- ✅ Credenciais em variáveis de ambiente
- ✅ HTTPS forçado
- ✅ Rate limiting para login
- ✅ Validação forte de senha
- ✅ Logging de segurança

### O que você PRECISA fazer:
- ⚠️ Gerar nova SECRET_KEY (passo 1)
- ⚠️ Criar novo usuário de BD com permissões restritas
- ⚠️ Mudar senha do BD
- ⚠️ Configurar SSL/TLS (certificado)
- ⚠️ Revisar logs periodicamente

## 🚀 Deploy

Depois de tudo configurado, siga o guia em `PRODUCAO.md`.

Ou em resumo:
```bash
# 1. Instalar deps
pip install -r requirements.txt

# 2. Migrações
python manage.py migrate

# 3. Coletar státicos
python manage.py collectstatic --noinput

# 4. Rodar com Gunicorn
gunicorn sistema_vendas.wsgi:application --bind 0.0.0.0:8000
```

## 🆘 Problemas?

1. Rodar `python validate_production.py` para ver o que está errado
2. Verificar arquivo `.env` está completo
3. Ver logs em `logs/security.log` e `logs/auth.log`

---

**Você está a 5 passos de coloca seu sistema em produção segura!** 🎉
