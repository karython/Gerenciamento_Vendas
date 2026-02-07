# app_controle/views/dashboard_views.py
"""
Dashboard com métricas e gráficos
"""

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import json
from ..models import Venda, Estoque
from ..services.auth_services import AuthService


@AuthService.requer_login
def dashboard(request):
    """Dashboard com dados reais do banco - OTIMIZADO"""
    
    loja = AuthService.loja_logada(request)
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    data_30_dias = hoje - timedelta(days=30)
    
    # ✅ Agregação única para dados do mês
    vendas_mes_agregado = Venda.objects.filter(
        data_venda__gte=inicio_mes  # ✅ Novo nome
    ).aggregate(
        receita_bruta=Sum('subtotal'),  # ✅ Novo nome
        receita_liquida=Sum('total'),   # ✅ Novo nome
        total_vendas=Count('id')
    )
    
    receita_bruta = vendas_mes_agregado['receita_bruta'] or 0
    receita_liquida = vendas_mes_agregado['receita_liquida'] or 0
    total_vendas = vendas_mes_agregado['total_vendas'] or 0
    
    # ✅ Total de itens em estoque
    total_estoque = Estoque.objects.aggregate(
        total=Sum('quantidade_disponivel')  # ✅ Novo nome
    )['total'] or 0
    
    # ✅ Dados para o gráfico (últimos 30 dias)
    # Construir manualmente por data para evitar casos onde TruncDate retorna None
    from collections import OrderedDict

    vendas_qs = Venda.objects.filter(
        data_venda__gte=data_30_dias
    ).only('id', 'data_venda').order_by('data_venda')

    vendas_por_dia = OrderedDict()
    for v in vendas_qs:
        if not v.data_venda:
            continue
        dia = v.data_venda.date()
        chave = dia.strftime('%d/%m')
        vendas_por_dia[chave] = vendas_por_dia.get(chave, 0) + 1

    datas_vendas = list(vendas_por_dia.keys())
    valores_vendas = list(vendas_por_dia.values())
    
    # ✅ Receita bruta vs líquida (últimos 30 dias)
    vendas_30_agregado = Venda.objects.filter(
        data_venda__gte=data_30_dias  # ✅ Novo nome
    ).aggregate(
        receita_bruta_30=Sum('subtotal'),
        receita_liquida_30=Sum('total')
    )
    
    receita_bruta_30 = vendas_30_agregado['receita_bruta_30'] or 0
    receita_liquida_30 = vendas_30_agregado['receita_liquida_30'] or 0
    
    # Serializar JSON para o template
    datas_vendas_json = mark_safe(json.dumps(datas_vendas, ensure_ascii=False))
    valores_vendas_json = mark_safe(json.dumps(valores_vendas, ensure_ascii=False))

    context = {
        'loja': loja,
        'receita_bruta': f"{receita_bruta:.2f}".replace('.', ','),
        'receita_liquida': f"{receita_liquida:.2f}".replace('.', ','),
        'total_vendas': total_vendas,
        'total_estoque': total_estoque,
        'datas_vendas_json': datas_vendas_json,
        'valores_vendas_json': valores_vendas_json,
        'receita_bruta_30': f"{receita_bruta_30:.2f}".replace('.', ','),
        'receita_liquida_30': f"{receita_liquida_30:.2f}".replace('.', ','),
    }
    
    return render(request, 'core/dashboard.html', context)