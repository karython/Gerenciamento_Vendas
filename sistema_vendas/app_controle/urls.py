# app_controle/urls.py
from django.urls import path
from .views import (
    cliente_views,
    dashboard_views,
    estoque_views,
    vendas_views,
    novavenda_views,
    home_views,
    logout_views
)

app_name = 'app_controle'

urlpatterns = [
    # Página inicial
    path('', home_views.home, name='home'),
    
    # Dashboard
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    
    # Clientes
    path('clientes/', cliente_views.listar_clientes, name='listar_clientes'),
    path('clientes/criar/', cliente_views.criar_cliente, name='criar_cliente'),
    path('clientes/editar/<int:id>/', cliente_views.editar_cliente, name='editar_cliente'),
    path('clientes/deletar/<int:id>/', cliente_views.deletar_cliente, name='deletar_cliente'),
    
    # Estoque
    path('estoque/', estoque_views.estoque, name='estoque'),
    
    # Vendas
    path('vendas/', vendas_views.vendas, name='vendas'),
    path('vendas/nova/', novavenda_views.nova_venda, name='nova_venda'),
    
    # Logout
    path('logout/', logout_views.logout, name='logout'),
]