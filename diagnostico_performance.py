#!/usr/bin/env python
"""
Script de diagnóstico de performance para o sistema de vendas
Detecta queries lentas, índices faltando e problemas de sessão
"""

import os
import django
import sys
from django.db import connection, reset_queries
from django.test.utils import override_settings
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_vendas.settings')
django.setup()

from app_controle.models import Loja
from django.contrib.sessions.models import Session

# Habilitar logging SQL
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)

print("=" * 80)
print("🔍 DIAGNÓSTICO DE PERFORMANCE - SISTEMA DE VENDAS")
print("=" * 80)

# ============================================================================
# 1. VERIFICAR ÍNDICES NO BANCO
# ============================================================================
print("\n[1] Verificando índices na tabela LOJA...")
print("-" * 80)

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT INDEX_NAME, COLUMN_NAME, SEQ_IN_INDEX, NON_UNIQUE
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'LOJA'
        ORDER BY INDEX_NAME, SEQ_IN_INDEX
    """)
    
    indices = cursor.fetchall()
    
    if not indices:
        print("❌ NENHUM ÍNDICE ENCONTRADO! Migração não foi aplicada.")
    else:
        print("✅ Índices encontrados:")
        for idx in indices:
            index_name, column, seq, non_unique = idx
            unique = "ÚNICO" if not non_unique else "COMPOSTO"
            print(f"   • {index_name}: {column} (seq={seq}) [{unique}]")

# ============================================================================
# 2. VERIFICAR PERFORMANCE DE QUERIES
# ============================================================================
print("\n[2] Testando performance de queries...")
print("-" * 80)

# Resetar queries
reset_queries()

# Habilitar o tracking de queries
with override_settings(DEBUG=True):
    try:
        # Query 1: Busca por CNPJ sem índice (simulado)
        print("\n📊 Query 1: Loja.objects.filter(ATIVO=True).first()")
        reset_queries()
        loja = Loja.objects.filter(ATIVO=True).first()
        
        if connection.queries:
            query_time = connection.queries[0].get('time', 'N/A')
            print(f"   ⏱️  Tempo: {query_time} segundos")
            print(f"   🔍 SQL: {connection.queries[0]['sql'][:100]}...")
        
        # Query 2: Busca por CNPJ (com índice)
        print("\n📊 Query 2: Loja.objects.only().filter(ATIVO=True).first()")
        reset_queries()
        loja = Loja.objects.only('idLOJA', 'ATIVO').filter(ATIVO=True).first()
        
        if connection.queries:
            query_time = connection.queries[0].get('time', 'N/A')
            print(f"   ⏱️  Tempo: {query_time} segundos")
            print(f"   🔍 SQL: {connection.queries[0]['sql'][:100]}...")
    
    except Exception as e:
        print(f"⚠️  Erro ao executar queries: {e}")

# ============================================================================
# 3. VERIFICAR CONFIGURAÇÃO DE SESSÃO
# ============================================================================
print("\n[3] Verificando configuração de sessão...")
print("-" * 80)

from django.conf import settings

session_config = {
    'SESSION_SAVE_EVERY_REQUEST': settings.SESSION_SAVE_EVERY_REQUEST,
    'SESSION_COOKIE_AGE': settings.SESSION_COOKIE_AGE,
    'SESSION_ENGINE': settings.SESSION_ENGINE,
    'SESSION_EXPIRE_AT_BROWSER_CLOSE': settings.SESSION_EXPIRE_AT_BROWSER_CLOSE,
}

for key, value in session_config.items():
    status = "✅" if (
        (key == 'SESSION_SAVE_EVERY_REQUEST' and not value) or
        (key != 'SESSION_SAVE_EVERY_REQUEST')
    ) else "❌"
    print(f"{status} {key}: {value}")

# ============================================================================
# 4. VERIFICAR SESSÕES ATIVAS NO BANCO
# ============================================================================
print("\n[4] Analisando sessões no banco...")
print("-" * 80)

try:
    total_sessions = Session.objects.count()
    print(f"   📊 Total de sessões: {total_sessions}")
    
    # Sessões mais antigas
    oldest = Session.objects.order_by('expire_date').first()
    if oldest:
        print(f"   📆 Sessão mais antiga: {oldest.expire_date}")
    
    # Tamanho médio das sessões
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                ROUND(AVG(CHAR_LENGTH(session_data))) as avg_size
            FROM django_session
        """)
        result = cursor.fetchone()
        total, avg_size = result
        print(f"   💾 Tamanho médio da sessão: {avg_size} bytes")
        
except Exception as e:
    print(f"⚠️  Não foi possível analisar sessões: {e}")

# ============================================================================
# 5. VERIFICAR CACHE
# ============================================================================
print("\n[5] Verificando configuração de cache...")
print("-" * 80)

cache_config = settings.CACHES.get('default', {})
print(f"   🔧 Backend: {cache_config.get('BACKEND', 'N/A')}")
print(f"   📍 Localização: {cache_config.get('LOCATION', 'N/A')}")

# ============================================================================
# 6. RECOMENDAÇÕES
# ============================================================================
print("\n[6] Recomendações:")
print("-" * 80)

recommendations = []

# Verificar índices
if not indices or not any('idx_loja_cnpj_ativo' in str(i) for i in indices):
    recommendations.append("❌ Aplicar migração 0014_performance_indexes.py")

# Verificar SESSION_SAVE_EVERY_REQUEST
if settings.SESSION_SAVE_EVERY_REQUEST:
    recommendations.append("❌ Desabilitar SESSION_SAVE_EVERY_REQUEST em settings.py")

# Verificar cache
if 'LocMemCache' in cache_config.get('BACKEND', ''):
    recommendations.append("⚠️  Usar Redis ou Memcached em produção (não LocMemCache)")

# Verificar DEBUG
if settings.DEBUG:
    recommendations.append("❌ Desabilitar DEBUG=True em produção")

if recommendations:
    for rec in recommendations:
        print(f"   {rec}")
else:
    print("   ✅ Nenhuma recomendação no momento!")

print("\n" + "=" * 80)
print("✅ Diagnóstico completo!")
print("=" * 80)
