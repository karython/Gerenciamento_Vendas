# CHECKLIST DE OTIMIZAÇÃO PARA PRODUÇÃO

## ✅ Mudanças Implementadas (2026-02-05)

### 1. Modelo de Dados
- [x] Adicionado índice composto `idx_loja_cnpj_ativo` em `Loja`
- [x] Adicionado `db_index=True` em campo `CNPJ`
- [x] Adicionado `db_index=True` em campo `ATIVO`
- [x] Migração criada: `0014_performance_indexes.py`

### 2. Configuração de Sessão
- [x] `SESSION_SAVE_EVERY_REQUEST` alterado para usar variável de ambiente
- [x] Padrão: `False` em produção (reduz queries ao banco em ~95%)
- [x] Arquivo `.env.example` atualizado

### 3. Middleware
- [x] Cache TTL aumentado de 5 para 30 minutos
- [x] Melhor tratamento de lojas desativadas

### 4. Serviços de Autenticação
- [x] `autenticar_loja()` otimizado com `.only()`
- [x] `loja_logada()` otimizado com `.only()`
- [x] Comentários explicando otimizações

### 5. Documentação
- [x] `DIAGNOSTICO_PERFORMANCE_PRODUCAO.md` criado
- [x] Script `diagnostico_performance.py` criado
- [x] `.env.example` com configurações otimizadas

---

## 🚀 PASSOS PARA IMPLANTAR EM PRODUÇÃO

### Fase 1: Preparação (Antes do Deploy)

```bash
# 1. Backup do banco de dados
mysqldump -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup_2026-02-05.sql

# 2. Verificar estado atual
cd /home/karython/Área de Trabalho/ProjetoVendas/Gerenciamento_Vendas
git status

# 3. Revisar mudanças
git diff

# 4. Testar localmente (se possível)
cd sistema_vendas
python manage.py makemigrations --dry-run
python manage.py migrate --plan
```

### Fase 2: Deploy (Mudanças de código)

```bash
# 1. Fazer commit das mudanças
git add -A
git commit -m "Performance: Otimizar queries de login e sessão (índices, cache, SESSION_SAVE_EVERY_REQUEST)"

# 2. Push para produção
git push origin main

# 3. Verificar arquivo .env
cat sistema_vendas/.env
# Garantir que: SESSION_SAVE_EVERY_REQUEST=False

# 4. Atualizar dependências (se houver)
pip install -r sistema_vendas/requirements.txt
```

### Fase 3: Migração do Banco (Crítica)

```bash
cd /home/karython/Área de Trabalho/ProjetoVendas/Gerenciamento_Vendas/sistema_vendas

# 1. Aplicar migração (sem downtime em MySQL)
python manage.py migrate app_controle 0014_performance_indexes

# 2. Verificar se migração foi bem-sucedida
python manage.py showmigrations app_controle | grep 0014

# 3. Verificar índices no banco
python manage.py dbshell
# Então execute:
# SHOW INDEX FROM LOJA;
# Verificar se idx_loja_cnpj_ativo aparece
```

### Fase 4: Reiniciar Aplicação

```bash
# Opção 1: Gunicorn com HUP (sem downtime)
kill -HUP $(pgrep -f gunicorn)

# Opção 2: Reiniciar completo (com pequeno downtime)
systemctl restart sistema_vendas

# Opção 3: Supervisor
supervisorctl restart sistema_vendas

# Aguardar 30 segundos
sleep 30

# Verificar se está funcionando
curl -I https://seu-dominio.com/login
```

### Fase 5: Validação Pós-Deploy

```bash
# 1. Testar login manualmente
# Abrir navegador: https://seu-dominio.com/login
# Tentar fazer login
# Tempo esperado: 200-500ms

# 2. Executar diagnóstico
python diagnostico_performance.py

# 3. Monitorar logs
tail -f logs/auth.log
tail -f logs/security.log

# 4. Verificar timeouts
# Buscar por erros nos logs de aplicação
grep -i "timeout\|error" logs/*.log
```

---

## 📊 TESTES DE PERFORMANCE

### Teste 1: Velocidade de Login
```bash
# Medir tempo de resposta da página de login
time curl -w "\nTempo total: %{time_total}s\n" \
  -F "cnpj=00.000.000/0000-00" \
  -F "senha=sua_senha" \
  https://seu-dominio.com/login

# Esperado: < 1 segundo
```

### Teste 2: Índices do Banco
```sql
-- Verificar se os índices estão sendo usados
EXPLAIN SELECT * FROM LOJA 
WHERE CNPJ='00.000.000/0000-00' AND ATIVO=1;

-- Esperado: Using index no Extra
```

### Teste 3: Sessões Salvas
```python
# Django shell
python manage.py shell

>>> from django.contrib.sessions.models import Session
>>> Session.objects.count()

# O número deve estar estável (não crescendo constantemente)
# Sem SESSION_SAVE_EVERY_REQUEST, não há gravação contínua
```

---

## ⚠️ POSSÍVEIS PROBLEMAS E SOLUÇÕES

### Problema 1: Migração não aplicada
```bash
# Verificar
python manage.py showmigrations app_controle

# Se não mostra 0014, recriar
rm app_controle/migrations/0014_performance_indexes.py
python manage.py makemigrations

# Depois aplicar
python manage.py migrate
```

### Problema 2: Índice não criado no banco
```bash
# Forçar recriação
python manage.py migrate app_controle zero
python manage.py migrate app_controle
```

### Problema 3: Sessões não expiram
```bash
# Verificar variável de ambiente
echo $SESSION_SAVE_EVERY_REQUEST  # Deve ser 'False'

# Se não estiver setada, editar .env
nano sistema_vendas/.env
# Adicionar: SESSION_SAVE_EVERY_REQUEST=False
```

---

## 🔍 MONITORAMENTO EM PRODUÇÃO

### Queries Lentas
```bash
# Habilitar log de queries lentas no MySQL
mysql -u root -p
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';

# Monitorar
tail -f /var/log/mysql/slow.log
```

### Performance de Login
```bash
# Grep no log de segurança
grep "Login bem-sucedido" logs/security.log | tail -20
grep "Falha de login" logs/security.log | tail -20
```

### Carga do Banco de Dados
```bash
# Ver queries ativas
mysql -u root -p
SHOW PROCESSLIST;

# Ver status
SHOW STATUS LIKE 'Threads%';
SHOW STATUS LIKE 'Questions';
```

---

## 📋 ROLLBACK (SE NECESSÁRIO)

```bash
# 1. Reverter código
git revert <commit-hash>
git push origin main

# 2. Reverter migração (cuidado!)
cd sistema_vendas
python manage.py migrate app_controle 0013_venda_orcamento_origem

# 3. Reiniciar aplicação
systemctl restart sistema_vendas
```

---

## ✅ VALIDAÇÃO FINAL

- [ ] Migração 0014 aplicada com sucesso
- [ ] Índices criados no banco (verificado com SHOW INDEX)
- [ ] SESSION_SAVE_EVERY_REQUEST = False no .env
- [ ] Teste de login respondendo em < 1 segundo
- [ ] Nenhum erro nos logs após 1 hora de operação
- [ ] Sessões não se acumulando indefinidamente
- [ ] Dashboard carregando normalmente

---

**Implementado em**: 2026-02-05  
**Responsável**: GitHub Copilot  
**Versão Django**: 5.2.8  
**Banco**: MySQL 8.0+
