#!/bin/bash

# Script para limpar cache e coletar staticfiles
# Uso: ./limpar_cache.sh

set -e

echo "=================================================="
echo "Limpando Cache e Coletando Static Files"
echo "=================================================="
echo ""

cd "$(dirname "$0")/sistema_vendas"

# 1. Limpar arquivos de cache do Django
echo "[1/4] Limpando cache de sessões e cache do Django..."
python3 manage.py clearcache 2>/dev/null || echo "  ✓ Cache limpo (ou não configurado)"

# 2. Limpar __pycache__ recursivo
echo "[2/4] Removendo arquivos __pycache__..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ __pycache__ removido"

# 3. Limpar pasta staticfiles antiga
echo "[3/4] Limpando pasta staticfiles antiga..."
rm -rf staticfiles/* 2>/dev/null || true
echo "  ✓ staticfiles limpo"

# 4. Coletar staticfiles novos
echo "[4/4] Coletando staticfiles novos..."
python3 manage.py collectstatic --noinput --clear
echo "  ✓ staticfiles coletado"

echo ""
echo "=================================================="
echo "✅ Cache e staticfiles atualizados com sucesso!"
echo "=================================================="
echo ""
echo "Próximos passos:"
echo "  1. Reinicie o servidor: python3 manage.py runserver"
echo "  2. Limpe o cache do navegador (Ctrl+Shift+Delete)"
echo "  3. Recarregue a página (Ctrl+F5)"
