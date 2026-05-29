# app_controle/views/dashboard_views.py
"""
Dashboard com métricas, gráficos e filtros dinâmicos
"""

from django.shortcuts import render
from django.http import JsonResponse
from collections import OrderedDict

from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json

from ..models import Venda, ItemVenda, Produto, Estoque
from ..services.auth_services import AuthService


def _parse_filtros(request):
    """
    Extrai e valida os parâmetros de filtro da requisição.
    Retorna (data_inicio, data_fim, produto_id).
    """
    hoje = timezone.now()

    data_inicio_str = request.GET.get('data_inicio', '').strip()
    data_fim_str    = request.GET.get('data_fim', '').strip()
    periodo         = request.GET.get('periodo', '30')
    produto_id      = request.GET.get('produto_id', '').strip()

    if data_inicio_str and data_fim_str:
        try:
            di = datetime.strptime(data_inicio_str, '%Y-%m-%d')
            df = datetime.strptime(data_fim_str,    '%Y-%m-%d')
            data_inicio = timezone.make_aware(di.replace(hour=0,  minute=0,  second=0))
            data_fim    = timezone.make_aware(df.replace(hour=23, minute=59, second=59))
        except ValueError:
            data_inicio = hoje - timedelta(days=30)
            data_fim    = hoje
    elif periodo == 'mes':
        data_inicio = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        data_fim    = hoje
    else:
        try:
            dias = int(periodo)
        except ValueError:
            dias = 30
        data_inicio = hoje - timedelta(days=dias)
        data_fim    = hoje

    produto_id = int(produto_id) if produto_id.isdigit() else None
    return data_inicio, data_fim, produto_id


@AuthService.requer_login
def dashboard(request):
    """Renderiza a página do dashboard com lista de produtos para o filtro."""
    loja = AuthService.loja_logada(request)

    produtos = Produto.objects.filter(ativo=True).only('id', 'descricao').order_by('descricao')

    return render(request, 'core/dashboard.html', {
        'loja': loja,
        'produtos': produtos,
    })


@AuthService.requer_login
def dashboard_api(request):
    """
    API JSON para o dashboard.
    Parâmetros GET:
        periodo       – '7', '30', '90', 'mes'  (padrão: '30')
        data_inicio   – 'YYYY-MM-DD'  (modo personalizado)
        data_fim      – 'YYYY-MM-DD'  (modo personalizado)
        produto_id    – int  (filtra gráfico de top produtos)
    """
    data_inicio, data_fim, produto_id = _parse_filtros(request)

    # ── Vendas no período ─────────────────────────────────────────────────────
    vendas_qs = Venda.objects.filter(
        data_venda__gte=data_inicio,
        data_venda__lte=data_fim,
    )

    agg = vendas_qs.aggregate(
        receita_bruta   = Sum('subtotal'),
        receita_liquida = Sum('total'),
        total_vendas    = Count('id'),
        total_desconto  = Sum('desconto'),
        total_frete     = Sum('frete'),
    )

    receita_bruta   = float(agg['receita_bruta']   or 0)
    receita_liquida = float(agg['receita_liquida'] or 0)
    total_vendas    = agg['total_vendas'] or 0
    total_desconto  = float(agg['total_desconto']  or 0)
    ticket_medio    = receita_liquida / total_vendas if total_vendas else 0

    # ── Vendas por dia (agrupamento Python — evita problema de TruncDate com MySQL sem tzinfo) ──
    vendas_raw = (
        vendas_qs
        .only('data_venda', 'total')
        .order_by('data_venda')
    )

    por_dia = OrderedDict()
    for v in vendas_raw:
        if not v.data_venda:
            continue
        chave = v.data_venda.astimezone(timezone.get_current_timezone()).date().strftime('%d/%m')
        if chave not in por_dia:
            por_dia[chave] = {'qtd': 0, 'receita': 0.0}
        por_dia[chave]['qtd']     += 1
        por_dia[chave]['receita'] += float(v.total or 0)

    labels_dias   = list(por_dia.keys())
    dados_qtd     = [d['qtd']     for d in por_dia.values()]
    dados_receita = [d['receita'] for d in por_dia.values()]

    # ── Top 5 produtos por receita ────────────────────────────────────────────
    itens_qs = ItemVenda.objects.filter(
        venda__data_venda__gte=data_inicio,
        venda__data_venda__lte=data_fim,
    )
    if produto_id:
        itens_qs = itens_qs.filter(produto_id=produto_id)

    top_produtos = list(
        itens_qs
        .values('produto__descricao')
        .annotate(
            qtd_total     = Sum('quantidade'),
            receita_total = Sum('total'),
        )
        .order_by('-receita_total')[:7]
    )

    labels_produtos  = [p['produto__descricao'] for p in top_produtos]
    dados_prod_rec   = [float(p['receita_total'] or 0) for p in top_produtos]
    dados_prod_qtd   = [float(p['qtd_total']     or 0) for p in top_produtos]

    # ── Distribuição por forma de pagamento ───────────────────────────────────
    formas = list(
        vendas_qs
        .values('forma_pagamento__nome')
        .annotate(count=Count('id'), receita=Sum('total'))
        .order_by('-receita')
    )

    labels_formas  = [f['forma_pagamento__nome'] or 'N/A' for f in formas]
    dados_formas   = [float(f['receita'] or 0) for f in formas]

    # ── Estoque total ─────────────────────────────────────────────────────────
    total_estoque = int(
        Estoque.objects.aggregate(t=Sum('quantidade_disponivel'))['t'] or 0
    )

    return JsonResponse({
        'kpis': {
            'receita_bruta':   receita_bruta,
            'receita_liquida': receita_liquida,
            'total_vendas':    total_vendas,
            'ticket_medio':    ticket_medio,
            'total_desconto':  total_desconto,
            'total_estoque':   total_estoque,
        },
        'vendas_dia': {
            'labels':   labels_dias,
            'qtd':      dados_qtd,
            'receita':  dados_receita,
        },
        'top_produtos': {
            'labels':  labels_produtos,
            'receita': dados_prod_rec,
            'qtd':     dados_prod_qtd,
        },
        'formas_pagamento': {
            'labels':  labels_formas,
            'receita': dados_formas,
        },
        'periodo': {
            'inicio': data_inicio.strftime('%d/%m/%Y'),
            'fim':    data_fim.strftime('%d/%m/%Y'),
        },
    })
