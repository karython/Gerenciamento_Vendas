# sistema_vendas/urls.py

from django.contrib import admin
from django.urls import path
from app_controle.views import (
    cliente_views,
    dashboard_views,
    estoque_views,
    vendas_views,
    novavenda_views,
    orcamento_views,
    home_views,
    logout_views,
    auth_views,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # === Autenticação (login e cadastro) ===
    path('', auth_views.index, name='index'),  # ← Página inicial (login)
    path('cadastro/', auth_views.cadastro, name='cadastro'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    
    # === DASHBOARD ===
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    
    # === ESTOQUE ===
    path('estoque/', estoque_views.estoque, name='estoque'),
    path('estoque/cadastrar/', estoque_views.cadastrar_produto, name='cadastrar_produto'),
    path('estoque/buscar/<int:produto_id>/', estoque_views.buscar_produto_ajax, name='buscar_produto_ajax'),
    path('estoque/editar/<int:produto_id>/', estoque_views.editar_produto, name='editar_produto'),
    path('estoque/deletar/<int:produto_id>/', estoque_views.deletar_produto, name='deletar_produto'),
    path('estoque/reposicao/<int:produto_id>/', estoque_views.adicionar_reposicao, name='adicionar_reposicao'),
    
    # === VENDAS ===
    path('vendas/', vendas_views.vendas, name='vendas'),
    path('vendas/nova/', novavenda_views.nova_venda, name='nova_venda'),  # ← Movido para cá
    path('vendas/criar/', novavenda_views.criar_venda, name='criar_venda'),
    path('vendas/pdf/<int:venda_id>/', novavenda_views.gerar_pdf_venda, name='gerar_pdf_venda'),
    path('vendas/deletar/<int:venda_id>/', vendas_views.deletar_venda, name='deletar_venda'),
    path('vendas/deletar-multiplas/', vendas_views.deletar_vendas_multiplas, name='deletar_vendas_multiplas'),
    
    # === ORÇAMENTOS ===
    path('orcamentos/novo/', orcamento_views.novo_orcamento, name='novo_orcamento'),
    path('orcamentos/criar/', orcamento_views.criar_orcamento, name='criar_orcamento'),
    path('orcamentos/status/<int:orcamento_id>/', orcamento_views.atualizar_status_orcamento, name='atualizar_status_orcamento'),
    path('orcamentos/converter/<int:orcamento_id>/', orcamento_views.converter_orcamento_venda, name='converter_orcamento_venda'),
    path('orcamentos/pdf/<int:orcamento_id>/', orcamento_views.gerar_pdf_orcamento, name='gerar_pdf_orcamento'),
    path('orcamentos/deletar/<int:orcamento_id>/', orcamento_views.deletar_orcamento, name='deletar_orcamento'),
    path('orcamentos/', orcamento_views.listar_orcamentos, name='orcamentos'),
    
    # === APIs ===
    path('api/clientes/', novavenda_views.buscar_clientes, name='buscar_clientes'),
    path('api/produtos/', novavenda_views.buscar_produtos, name='buscar_produtos'),
    path('api/formas-pagamento/', novavenda_views.buscar_formas_pagamento, name='buscar_formas_pagamento'),
    path('api/orcamento/clientes/', orcamento_views.buscar_clientes, name='buscar_clientes_orcamento'),
    path('api/orcamento/produtos/', orcamento_views.buscar_produtos, name='buscar_produtos_orcamento'),
    path('api/orcamento/formas-pagamento/', orcamento_views.buscar_formas_pagamento, name='buscar_formas_pagamento_orcamento'),
    
    # === CLIENTES ===
    path('clientes/', cliente_views.listar_clientes, name='clientes'),
    path('clientes/criar/', cliente_views.criar_cliente, name='criar_cliente'),
    path('clientes/editar/<int:id>/', cliente_views.editar_cliente, name='editar_cliente'),
    path('clientes/deletar/<int:id>/', cliente_views.deletar_cliente, name='deletar_cliente'),
]