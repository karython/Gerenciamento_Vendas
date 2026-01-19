# app_controle/views/vendas_views.py

from django.shortcuts import render
from datetime import datetime
from ..services.venda_services import VendaService

def vendas(request):
    """Lista todas as vendas com filtro por data"""
    print("[VIEW] Carregando histórico de vendas...")
    
    # Obter parâmetros de filtro
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Buscar vendas com ou sem filtro
    vendas_lista = VendaService.listar_vendas(
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    
    print(f"[VIEW] Total de vendas encontradas: {vendas_lista.count()}")
    
    if data_inicio or data_fim:
        print(f"[VIEW] Filtros aplicados - Início: {data_inicio}, Fim: {data_fim}")
    
    context = {
        'vendas': vendas_lista,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    
    return render(request, 'vendas.html', context)