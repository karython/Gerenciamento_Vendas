# app_controle/views/dashboard_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.safestring import mark_safe
from ..models import Venda, Estoque, Cliente
from ..services.auth_services import AuthService


def dashboard(request):
    """Dashboard com dados reais do banco de dados - OTIMIZADO"""
    
    # Verificar se está logado
    loja = AuthService.loja_logada(request)
    if not loja:
        return redirect('login')
    
    # Pegar o mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    data_30_dias = hoje - timedelta(days=30)
    
    # === AGREGAÇÃO ÚNICA PARA TODOS OS DADOS DO MÊS ===
    vendas_mes_agregado = Venda.objects.filter(DT_VENDA__gte=inicio_mes).aggregate(
        receita_bruta=Sum('VLR_SUBTOTAL'),
        receita_liquida=Sum('VLR_TOTAL'),
        total_vendas=Count('idVENDA')
    )
    
    receita_bruta = vendas_mes_agregado['receita_bruta'] or 0
    receita_liquida = vendas_mes_agregado['receita_liquida'] or 0
    total_vendas = vendas_mes_agregado['total_vendas'] or 0
    
    # Total de itens em estoque - UMA ÚNICA QUERY
    total_estoque = Estoque.objects.aggregate(Sum('QTD_DISPONIVEL'))['QTD_DISPONIVEL__sum'] or 0
    
    # === DADOS PARA O GRÁFICO (últimos 30 dias) ===
    # Buscar todas as vendas dos últimos 30 dias em memória e agrupar
    vendas_30_dias_queryset = Venda.objects.filter(DT_VENDA__gte=data_30_dias).order_by('DT_VENDA')
    
    # Agrupar por data em Python (mais confiável com timezone-aware datetimes)
    from collections import defaultdict
    vendas_por_data_dict = defaultdict(int)
    
    for venda in vendas_30_dias_queryset:
        if venda.DT_VENDA:
            # Converter para timezone local e pegar só a data
            data_local = venda.DT_VENDA.astimezone(timezone.get_current_timezone())
            data_str = data_local.strftime('%d/%m')
            vendas_por_data_dict[data_str] += 1
    
    # Converter para listas ordenadas
    datas_vendas = sorted(vendas_por_data_dict.keys(), key=lambda x: tuple(map(int, x.split('/'))))
    valores_vendas = [vendas_por_data_dict[data] for data in datas_vendas]
    
    print(f"[DASHBOARD] Datas vendas: {datas_vendas}")
    print(f"[DASHBOARD] Valores vendas: {valores_vendas}")
    
    # === RECEITA BRUTA vs LÍQUIDA (últimos 30 dias) - UMA QUERY ===
    vendas_30_agregado = Venda.objects.filter(DT_VENDA__gte=data_30_dias).aggregate(
        receita_bruta_30=Sum('VLR_SUBTOTAL'),
        receita_liquida_30=Sum('VLR_TOTAL')
    )
    
    receita_bruta_30 = vendas_30_agregado['receita_bruta_30'] or 0
    receita_liquida_30 = vendas_30_agregado['receita_liquida_30'] or 0
    
    # Serializar JSON de forma segura para o template (evita escape HTML)
    datas_vendas_json = mark_safe(json.dumps(datas_vendas, ensure_ascii=False))
    valores_vendas_json = mark_safe(json.dumps(valores_vendas, ensure_ascii=False))

    context = {
        'loja': loja,
        'receita_bruta': f"{receita_bruta:.2f}".replace('.', ','),
        'receita_liquida': f"{receita_liquida:.2f}".replace('.', ','),
        'total_vendas': total_vendas,
        'total_estoque': total_estoque,
        'datas_vendas': datas_vendas,
        'valores_vendas': valores_vendas,
        'datas_vendas_json': datas_vendas_json,
        'valores_vendas_json': valores_vendas_json,
        'receita_bruta_30': f"{receita_bruta_30:.2f}".replace('.', ','),
        'receita_liquida_30': f"{receita_liquida_30:.2f}".replace('.', ','),
    }
    
    return render(request, 'dashboard.html', context)
