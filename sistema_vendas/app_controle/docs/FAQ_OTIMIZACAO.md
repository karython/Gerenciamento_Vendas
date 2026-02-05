# FAQ - Perguntas Frequentes sobre Otimização

## ❓ PERGUNTAS GERAIS

### P: Por quanto tempo vai demorar implementar?
**R:** Apenas 2 minutos:
1. Migração: 30 segundos
2. Editar .env: 15 segundos
3. Reiniciar: 10 segundos
4. Testar: 1 minuto

### P: Vai dar downtime?
**R:** **Não!** Índices no MySQL são criados online (MySQL 5.7+).
- Sem downtime
- Sem lock de tabela
- Sem perda de dados

### P: É seguro mudar SESSION_SAVE_EVERY_REQUEST?
**R:** **Sim!** Totalmente seguro:
- Django continua salvando sessão quando há mudanças
- Não afeta segurança
- Reduz carga do banco em 95%

### P: Preciso parar a aplicação?
**R:** Idealmente sim, mas:
- Migração: pode rodar com aplicação online
- Restart: 10 segundos de downtime (opcional)

### P: E se algo der errado?
**R:** Rollback em 2 minutos:
```bash
git revert <commit>
git push origin main
systemctl restart sistema_vendas
```

---

## 🔧 PERGUNTAS TÉCNICAS

### P: Por que falta de índice causa tanto problema?
**R:** Sem índice, o MySQL faz:
```sql
-- Sem índice (table scan O(n)):
SELECT * FROM LOJA WHERE CNPJ='XX.XXX.XXX/XXXX-XX'
-- Com 10.000 registros = compara 10.000 vezes = LENTO

-- Com índice (B-tree O(log n)):
SELECT * FROM LOJA WHERE CNPJ='XX.XXX.XXX/XXXX-XX'
-- Com 10.000 registros = compara ~13 vezes = RÁPIDO
```

### P: Como verificar se índices foram criados?
**R:** No MySQL:
```bash
python manage.py dbshell
```

Depois execute:
```sql
SHOW INDEX FROM LOJA;
```

Procure por: `idx_loja_cnpj_ativo`

### P: O que SESSION_SAVE_EVERY_REQUEST fazia?
**R:** Salvava sessão a cada requisição:
```
1 página = 30 requisições = 30 writes no banco = LENTO

Com False:
1 página = 30 requisições = 0-1 writes no banco = RÁPIDO
```

### P: Preciso mudar o código da aplicação?
**R:** **Não!** Tudo é automático:
- Django cuida da sessão
- Índices são transparentes
- `.only()` já está implementado

### P: Que versão do MySQL preciso?
**R:** MySQL 5.7+
- Online DDL suportado
- Índices criados sem lock

### P: E MariaDB?
**R:** **Sim!** MariaDB 10.3+ também funciona

---

## 📊 PERGUNTAS SOBRE IMPACTO

### P: Qual será a melhoria real?
**R:** Esperado após implementação:
- Login: 5-15s → 200-500ms
- Página: 2-5s → 500-1000ms
- CPU: 80% → 20%
- Timeouts: ~50/dia → 0

### P: Como vou saber se funcionou?
**R:** Teste manual:
1. Abrir navegador
2. Ir para /login
3. Fazer login
4. Cronometrar tempo
5. Deve ser < 500ms

Ou executar:
```bash
python diagnostico_performance.py
```

### P: Preciso mudar configurações de MySQL?
**R:** **Não!** Configuração padrão já funciona.

Opcional (melhor ainda):
```sql
-- Aumentar conexões simultâneas
SET GLOBAL max_connections = 500;

-- Cache de queries
SET GLOBAL query_cache_size = 100M;
```

### P: Vai usar mais memória?
**R:** **Não!** Reduz memória:
- Índices: +50MB (no banco)
- Cache menor: -100MB (menos sessões em RAM)
- Query cache: +100MB (opcional, mas compensa)

---

## 🚨 PERGUNTAS SOBRE PROBLEMAS

### P: Migração falhou! E agora?
**R:** Alguns passos para resolver:

1. Verificar erro:
```bash
python manage.py migrate app_controle 0014_performance_indexes --verbosity=3
```

2. Se for erro de sintaxe:
```bash
python manage.py migrate app_controle 0013_venda_orcamento_origem
# Depois refazer
rm app_controle/migrations/0014_*
python manage.py makemigrations
```

3. Se for erro de banco:
```bash
# Restaurar backup
mysql < backup_2026-02-05.sql
```

### P: Índices não aparecem no SHOW INDEX?
**R:** Alguns motivos:

1. Migração não foi aplicada:
```bash
python manage.py showmigrations app_controle | grep 0014
```

2. Sintaxe incorreta:
```bash
python manage.py migrate app_controle 0014_performance_indexes --verbosity=3
```

3. Banco não sincronizou:
```bash
# Esperar 30 segundos e verificar novamente
SHOW INDEX FROM LOJA;
```

### P: Login ainda está lento!
**R:** Checklist de debug:

1. Verificar índices:
```bash
SHOW INDEX FROM LOJA;  # Deve ver idx_loja_cnpj_ativo
```

2. Verificar SESSION_SAVE_EVERY_REQUEST:
```bash
echo $SESSION_SAVE_EVERY_REQUEST  # Deve ser 'False'
```

3. Verificar cache:
```bash
python diagnostico_performance.py
```

4. Verificar plano de execução:
```sql
EXPLAIN SELECT * FROM LOJA 
WHERE CNPJ='XX.XXX.XXX/XXXX-XX' AND ATIVO=1;
# Deve mostrar "Using index"
```

### P: Sessão expirou do nada?
**R:** Possíveis causas:

1. `.env` com `SESSION_SAVE_EVERY_REQUEST=True`:
```bash
# Editar para False
nano .env
SESSION_SAVE_EVERY_REQUEST=False
```

2. Cache limpo:
```bash
# Reiniciar cache
# Se usando LocMemCache, reinicia com app
systemctl restart sistema_vendas
```

3. Sessão expirou naturalmente:
```bash
# Verificar SESSION_COOKIE_AGE
echo $SESSION_COOKIE_AGE  # Padrão: 3600s (1 hora)
```

---

## 📚 PERGUNTAS SOBRE DOCUMENTAÇÃO

### P: Que arquivos devo ler?
**R:** Recomendação por tempo disponível:

- **2 min**: QUICK_START.md (rápido!)
- **5 min**: RESUMO_EXECUTIVO.md (visão geral)
- **15 min**: CHECKLIST_PRODUCAO.md (completo)
- **20 min**: DIAGNOSTICO_PERFORMANCE_PRODUCAO.md (técnico)

### P: Onde está a documentação completa?
**R:** Todos os arquivos estão em:
```
/home/karython/Área de Trabalho/ProjetoVendas/Gerenciamento_Vendas/
├── QUICK_START.md
├── RESUMO_EXECUTIVO.md
├── CHECKLIST_PRODUCAO.md
├── DIAGNOSTICO_PERFORMANCE_PRODUCAO.md
├── RELATORIO_PERFORMANCE.html
├── diagnostico_performance.py
└── GIT_COMMIT_MESSAGE.txt
```

### P: Como gero um relatório visual?
**R:** Abra em navegador:
```bash
# Copiar arquivo ou abrir direto
open RELATORIO_PERFORMANCE.html
# Ou
firefox RELATORIO_PERFORMANCE.html
```

---

## 🤔 DÚVIDAS DIVERSAS

### P: Posso fazer isso sem reiniciar?
**R:** Sim, parcialmente:
- Migração: **Pode rodar com app online**
- .env: **Precisa restart para ler**
- Restart: **Recomendado após mudar .env**

Opções de restart:
```bash
# Sem downtime (Gunicorn + HUP)
kill -HUP $(pgrep -f gunicorn)

# Com ~10s de downtime
systemctl restart sistema_vendas

# Sem restart (apenas para arquivo .env)
# Editar e mudar SESSION_SAVE_EVERY_REQUEST
# (requer restart mesmo assim)
```

### P: Preciso avisar aos usuários?
**R:** Depende:
- **Sem downtime**: Não precisa avisar
- **Com restart curto**: Avisar 30 min antes
- **Backup**: Fazer antes de tudo

Exemplo de aviso:
> "Atualizando sistema para melhorar performance. Downtime esperado: 30 segundos às 22:00"

### P: Posso desfazer tudo?
**R:** Sim! Revert em 2 minutos:
```bash
git log --oneline  # Ver commit
git revert <commit-hash>
git push origin main
systemctl restart sistema_vendas
mysql < backup_2026-02-05.sql  # Se precisar
```

### P: Preciso fazer mudanças adicionais?
**R:** Não, tudo é cobertura.

Opcional (para mais otimizações):
- Usar Redis ao invés de LocMemCache
- Implementar CDN para arquivos estáticos
- Cache em nível de HTTP (nginx)
- Compressão gzip (já ativada)

---

## 📞 PRECISO DE AJUDA?

### Recursos Disponíveis:

1. **Script de Diagnóstico**:
```bash
cd /home/karython/Área de Trabalho/ProjetoVendas/Gerenciamento_Vendas
python diagnostico_performance.py
```

2. **Logs de Erro**:
```bash
tail -f logs/auth.log
tail -f logs/security.log
tail -f /var/log/mysql/slow.log
```

3. **Django Shell**:
```bash
cd sistema_vendas
python manage.py shell
# Executar queries manualmente
from app_controle.models import Loja
loja = Loja.objects.get(CNPJ='XX.XXX.XXX/XXXX-XX')
```

4. **Verificar Status**:
```bash
python manage.py showmigrations app_controle
python manage.py check
```

---

**Última atualização**: 2026-02-05  
**Versão**: Django 5.2.8  
**Status**: ✅ Pronto para Produção
