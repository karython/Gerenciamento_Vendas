#!/bin/bash

# Script de Instalação Rápida para Produção

echo "=========================================="
echo "Instalação Rápida - Sistema de Vendas"
echo "=========================================="
echo ""

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "📦 Criando virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment criado"
fi

echo "🔌 Ativando virtual environment..."
source venv/bin/activate

echo "📥 Instalando dependências..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "✓ Instalação concluída!"
echo ""
echo "=========================================="
echo "Próximos passos:"
echo "=========================================="
echo ""
echo "1. Editar arquivo .env com suas configurações:"
echo "   nano .env"
echo ""
echo "2. Gerar nova SECRET_KEY:"
echo "   python manage.py shell"
echo "   from django.core.management.utils import get_random_secret_key"
echo "   print(get_random_secret_key())"
echo ""
echo "3. Validar configurações:"
echo "   python validate_production.py"
echo ""
echo "4. Rodar migrações:"
echo "   python manage.py migrate"
echo ""
echo "5. Iniciar servidor:"
echo "   python manage.py runserver"
echo ""
echo "=========================================="
