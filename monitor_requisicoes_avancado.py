#!/usr/bin/env python
"""
Monitor Avançado de Requisições ao Banco de Dados
Rastreia queries lentas e gera relatórios detalhados
"""

import os
import django
import sys
from django.db import connection, reset_queries
from django.test.utils import override_settings
import logging
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_vendas.settings')
django.setup()

from app_controle.models import Loja, Venda, Orcamento, Cliente, Produto, Pagamento, ItemVenda
from django.contrib.sessions.models import Session

print("=" * 90)
print("🚀 MONITOR AVANÇADO DE REQUISIÇÕES AO BANCO DE DADOS")
print("=" * 90)

# ============================================================================
# ANALISAR QUERIES LENTAS
# ============================================================================
print("\n[1] Identificando Queries Lentas (> 0.1s)...")
print("-" * 90)

SLOW_QUERY_THRESHOLD = 0.1  # 100ms

with override_settings(DEBUG=True):
    # Teste intensivo com múltiplas operações
    queries_report = []
    
    operations = [
        ("Loja - Listar todas", Loja.objects.all()),
        ("Loja - Filtrar ativos", Loja.objects.filter(ATIVO=True)),
        ("Loja - Apenas IDs", Loja.objects.values_list('idLOJA')),
        ("Venda - Listar todas", Venda.objects.all()),
        ("Venda - Com cliente", Venda.objects.select_related('CLIENTE_idCLIENTE')),
        ("Venda - Apenas total", Venda.objects.values('idVENDA', 'VLR_TOTAL')),
        ("Orcamento - Listar todos", Orcamento.objects.all()),
        ("Cliente - Listar todos", Cliente.objects.all()),
        ("Produto - Listar todos", Produto.objects.all()),
        ("ItemVenda - Listar todos", ItemVenda.objects.all()),
    ]
    
    slow_queries_found = []
    
    print(f"\n{'Operação':<40} {'Tempo (ms)':<15} {'Status':<20}")
    print("-" * 90)
    
    for description, queryset in operations:
        reset_queries()
        try:
            # Executar a query
            list(queryset)
            
            if connection.queries:
                total_time = sum(float(q.get('time', 0)) for q in connection.queries)
                total_ms = total_time * 1000
                
                # Verificar se é lenta
                is_slow = total_ms > (SLOW_QUERY_THRESHOLD * 1000)
                status = "🔴 LENTA" if is_slow else "✅ OK"
                
                print(f"{description:<40} {total_ms:>10.2f} ms  {status:<20}")
                
                if is_slow:
                    slow_queries_found.append({
                        'description': description,
                        'time_ms': total_ms,
                        'num_queries': len(connection.queries),
                        'queries': connection.queries
                    })
                
                queries_report.append({
                    'description': description,
                    'time_ms': total_ms,
                    'num_queries': len(connection.queries)
                })
        except Exception as e:
            print(f"{description:<40} ERRO: {str(e)[:30]:<20}")

# ============================================================================
# DETALHES DAS QUERIES LENTAS
# ============================================================================
if slow_queries_found:
    print("\n" + "=" * 90)
    print("🔴 QUERIES LENTAS ENCONTRADAS")
    print("=" * 90)
    
    for idx, slow_query in enumerate(slow_queries_found, 1):
        print(f"\n[{idx}] {slow_query['description']}")
        print(f"    ⏱️  Tempo Total: {slow_query['time_ms']:.2f}ms")
        print(f"    📊 Número de Queries: {slow_query['num_queries']}")
        print(f"    📋 Detalhes:")
        
        for q_idx, query in enumerate(slow_query['queries'], 1):
            q_time = float(query.get('time', 0))
            q_ms = q_time * 1000
            sql = query['sql']
            
            # Truncar SQL para melhor visualização
            if len(sql) > 120:
                sql_display = sql[:120] + "..."
            else:
                sql_display = sql
            
            print(f"       {q_idx}. [{q_ms:.2f}ms] {sql_display}")

# ============================================================================
# ANÁLISE DE CAMPOS DESNECESSÁRIOS
# ============================================================================
print("\n" + "=" * 90)
print("🎯 OTIMIZAÇÃO: Impacto de usar .only() ou .defer()")
print("=" * 90)

with override_settings(DEBUG=True):
    # Comparação 1: Loja com todos os campos vs apenas campos essenciais
    print("\n[Teste 1] Loja.objects.all() - Comparação")
    print("-" * 90)
    
    reset_queries()
    list(Loja.objects.all())
    time_full = sum(float(q.get('time', 0)) for q in connection.queries) * 1000
    size_full = sum(len(q['sql']) for q in connection.queries)
    
    reset_queries()
    list(Loja.objects.only('idLOJA', 'NOME_LOJA', 'ATIVO'))
    time_only = sum(float(q.get('time', 0)) for q in connection.queries) * 1000
    size_only = sum(len(q['sql']) for q in connection.queries)
    
    improvement = ((time_full - time_only) / time_full * 100) if time_full > 0 else 0
    
    print(f"Todos os campos:     {time_full:>10.2f}ms  |  SQL size: {size_full:>6} chars")
    print(f"Apenas essenciais:   {time_only:>10.2f}ms  |  SQL size: {size_only:>6} chars")
    print(f"⚡ Melhoria:         {improvement:>10.1f}%")
    
    # Comparação 2: Venda com select_related vs sem
    print("\n[Teste 2] Venda.objects - Comparação com select_related")
    print("-" * 90)
    
    reset_queries()
    list(Venda.objects.all())
    time_without = sum(float(q.get('time', 0)) for q in connection.queries) * 1000
    count_without = len(connection.queries)
    
    reset_queries()
    list(Venda.objects.select_related('CLIENTE_idCLIENTE'))
    time_with = sum(float(q.get('time', 0)) for q in connection.queries) * 1000
    count_with = len(connection.queries)
    
    print(f"Sem select_related:  {time_without:>10.2f}ms  |  {count_without} queries")
    print(f"Com select_related:  {time_with:>10.2f}ms  |  {count_with} queries")
    print(f"⚡ Impacto:          {(time_with - time_without):+.2f}ms")

# ============================================================================
# ESTATÍSTICAS GERAIS
# ============================================================================
print("\n" + "=" * 90)
print("📊 RESUMO ESTATÍSTICO")
print("=" * 90)

if queries_report:
    times = [q['time_ms'] for q in queries_report]
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    total_queries = sum(q['num_queries'] for q in queries_report)
    
    print(f"\nTotal de operações testadas: {len(queries_report)}")
    print(f"Total de queries executadas: {total_queries}")
    print(f"\nTempo Médio:  {avg_time:>10.2f}ms")
    print(f"Tempo Máximo: {max_time:>10.2f}ms")
    print(f"Tempo Mínimo: {min_time:>10.2f}ms")
    
    # Encontrar operação mais rápida e mais lenta
    fastest = min(queries_report, key=lambda x: x['time_ms'])
    slowest = max(queries_report, key=lambda x: x['time_ms'])
    
    print(f"\n✅ Operação mais rápida:  {fastest['description']} ({fastest['time_ms']:.2f}ms)")
    print(f"🔴 Operação mais lenta:   {slowest['description']} ({slowest['time_ms']:.2f}ms)")

# ============================================================================
# RECOMENDAÇÕES PERSONALIZADAS
# ============================================================================
print("\n" + "=" * 90)
print("💡 RECOMENDAÇÕES PERSONALIZADAS")
print("=" * 90)

recommendations = []

if slow_queries_found:
    recommendations.append("❌ Otimizar as seguintes queries lentas:")
    for sq in slow_queries_found:
        recommendations.append(f"   • {sq['description']}")

# Verificar tamanho de resultados
reset_queries()
loja_count = Loja.objects.count()
if loja_count > 100:
    recommendations.append("⚠️  Implementar paginação para listas grandes (>100 registros)")

recommendations.append("✅ Usar .only() para limitar campos em listagens")
recommendations.append("✅ Usar select_related() para relacionamentos ForeignKey")
recommendations.append("✅ Usar prefetch_related() para relacionamentos ManyToMany")
recommendations.append("✅ Implementar cache com Redis para dados frequentes")
recommendations.append("✅ Monitorar queries em desenvolvimento com django-debug-toolbar")

print()
for rec in recommendations:
    print(f"{rec}")

print("\n" + "=" * 90)
print("✅ Análise Completa! " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 90)
