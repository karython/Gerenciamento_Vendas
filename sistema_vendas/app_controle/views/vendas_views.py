# app_controle/views/vendas_views.py

from django.shortcuts import render
from ..services.venda_services import VendaService

def vendas(request):
    """Lista todas as vendas do banco de dados"""
    print("[VIEW] Carregando histórico de vendas...")
    vendas_lista = VendaService.listar_vendas()
    print(f"[VIEW] Total de vendas: {vendas_lista.count()}")
    return render(request, 'vendas.html', {'vendas': vendas_lista})