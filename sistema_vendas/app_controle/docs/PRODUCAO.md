# 🚀 Guia de Produção - Sistema de Vendas

**Data:** 5 de fevereiro de 2026  
**Versão:** 1.0.0

---

## 📋 Checklist Pré-Produção

### ✅ Segurança

- [x] SECRET_KEY movida para variável de ambiente (.env)
- [x] DEBUG desabilitado (DEBUG=False)
- [x] ALLOWED_HOSTS configurável
- [x] Credenciais do banco em variáveis de ambiente
- [x] HTTPS forçado em produção
- [x] Cookies seguros (HTTPS only)
- [x] HSTS habilitado
- [x] Rate limiting implementado para login
- [x] Validação forte de senhas (12+ caracteres)
- [x] Logging de segurança configurado
- [x] Decorator @requer_login em views protegidas

### ✅ Dependências

- [x] python-dotenv adicionado ao requirements.txt
- [x] Arquivo .env.example criado (para documentação)
- [x] .env adicionado ao .gitignore

---

## 🔧 Configuração para Produção

### Passo 1: Preparar o Servidor

```bash
# Atualizar sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependências do Python
sudo apt-get install -y python3 python3-pip python3-venv

# Clonar repositório
cd /var/www
git clone seu-repositorio.git sistema_vendas
cd sistema_vendas
```

### Passo 2: Criar Ambiente Virtual

```bash
# Criar virtual environment
python3 -m venv venv

# Ativar virtual environment
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### Passo 3: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env com valores de produção
nano .env
```

**Valores críticos a configurar:**

```env
# 1. Gerar nova SECRET_KEY (MUITO IMPORTANTE!)
SECRET_KEY=<gerar-novo-valor>

# 2. Desabilitar DEBUG
DEBUG=False

# 3. Configurar domínios
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com

# 4. Credenciais do banco (usar usuário com permissões restritas)
DB_ENGINE=django.db.backends.mysql
DB_NAME=prod_vendas
DB_USER=prod_user
DB_PASSWORD=<SENHA_SUPER_SEGURA>
DB_HOST=seu-host-db
DB_PORT=3306

# 5. HTTPS (deve estar com True em produção)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Passo 5: Executar Migrações

```bash
python manage.py migrate
```

### Passo 6: Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### Passo 7: Criar Superusuário (Opcional)

```bash
python manage.py createsuperuser
```

---

## 🏃 Executar em Produção

### Opção A: Gunicorn (Recomendado)

```bash
# Instalar gunicorn (já está em requirements.txt)
pip install gunicorn

# Executar com Gunicorn
gunicorn sistema_vendas.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60
```

### Opção B: Com Systemd (Recomendado para servidor)

Criar arquivo `/etc/systemd/system/vendas.service`:

```ini
[Unit]
Description=Sistema de Vendas Django
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/sistema_vendas
ExecStart=/var/www/sistema_vendas/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/sistema_vendas/vendas.sock \
    --timeout 60 \
    sistema_vendas.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl start vendas
sudo systemctl enable vendas  # Inicia na boot
```

---

## 🔒 Configurar Nginx como Reverse Proxy

Arquivo `/etc/nginx/sites-available/vendas`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;
    
    # SSL (usar certbot com Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://unix:/var/www/sistema_vendas/vendas.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/sistema_vendas/staticfiles/;
    }
}
```

Ativar:

```bash
sudo ln -s /etc/nginx/sites-available/vendas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Configurar SSL com Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot certonly --nginx -d seu-dominio.com -d www.seu-dominio.com
```

---

## 📊 Monitoramento e Logs

### Ver logs do serviço

```bash
sudo journalctl -u vendas -f  # Follow logs
sudo journalctl -u vendas -n 100  # Últimas 100 linhas
```

### Logs de segurança da aplicação

```bash
# Location dos logs (conforme settings.py)
tail -f /var/www/sistema_vendas/logs/security.log
tail -f /var/www/sistema_vendas/logs/auth.log
```

---

## 🔐 Boas Práticas de Segurança

### 1. Proteger arquivo .env

```bash
chmod 600 /var/www/sistema_vendas/.env
chown www-data:www-data /var/www/sistema_vendas/.env
```

### 2. Fazer backup do banco regularmente

```bash
# Script de backup (cron job)
#!/bin/bash
BACKUP_DIR="/backups/mysql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_USER="prod_user"
DB_NAME="prod_vendas"
DB_PASSWORD="$DB_PASSWORD"  # Carregar de arquivo seguro

mysqldump -u $DB_USER -p"$DB_PASSWORD" $DB_NAME | gzip > "$BACKUP_DIR/backup_$TIMESTAMP.sql.gz"

# Keepar apenas os últimos 30 dias
find "$BACKUP_DIR" -mtime +30 -delete
```

### 3. Monitorar tentativas de login falhadas

```bash
# Verificar ataques de força bruta
grep "Tentativa de login falhada\|Rate limit" /var/www/sistema_vendas/logs/auth.log
```

### 4. Atualizar Django regularmente

```bash
pip list --outdated
pip install --upgrade Django
```

---

## 🧪 Testes Antes de Produção

```bash
# Executar teste de segurança Django
python manage.py check --deploy

# Testes unitários
python manage.py test

# Cobertura de testes
coverage run --source='.' manage.py test
coverage report
```

---

## 🆘 Troubleshooting

### Erro: "SECRET_KEY não configurada"
- Solução: Configurar variável de ambiente `SECRET_KEY` no arquivo `.env`

### Erro: "Credenciais do banco inválidas"
- Solução: Verificar arquivo `.env` - DB_USER, DB_PASSWORD, DB_HOST

### Erro: "ALLOWED_HOSTS vazio"
- Solução: Configurar domínios em `ALLOWED_HOSTS` no `.env`

### Rate limit muito restritivo
- Editar `/app_controle/utils/security.py` - aumentar `MAX_ATTEMPTS` e `LOCKOUT_TIME`

---

## 📞 Suporte

Para problemas, verificar:
1. Logs em `/var/www/sistema_vendas/logs/`
2. Django error page (desabilitar DEBUG apenas em produção)
3. Nginx error log: `/var/log/nginx/error.log`

---

**Última atualização:** 5 de fevereiro de 2026
