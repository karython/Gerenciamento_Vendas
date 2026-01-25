# Importar todas as views dos módulos
from .auth_views import index, cadastro, login, logout
from .home_views import home, dashboard
from .cliente_views import (
    listar_clientes,
    criar_cliente,
    editar_cliente,
    deletar_cliente
)
from .estoque_views import (
    estoque,
    cadastrar_produto,
    buscar_produto_ajax,
    editar_produto,
    deletar_produto,
    adicionar_reposicao
)
from .vendas_views import vendas, deletar_venda
from .novavenda_views import (
    nova_venda,
    buscar_clientes,
    buscar_produtos,
    buscar_formas_pagamento,
    criar_venda,
    gerar_pdf_venda
)
from .orcamento_views import (
    novo_orcamento,
    criar_orcamento,
    buscar_clientes as buscar_clientes_orcamento,
    buscar_produtos as buscar_produtos_orcamento,
    buscar_formas_pagamento as buscar_formas_pagamento_orcamento
)

__all__ = [
    # Auth
    'index', 'cadastro', 'login', 'logout',
    # Home
    'home', 'dashboard',
    # Clientes
    'listar_clientes', 'criar_cliente', 'editar_cliente', 'deletar_cliente',
    # Estoque
    'estoque', 'cadastrar_produto', 'buscar_produto_ajax', 
    'editar_produto', 'deletar_produto', 'adicionar_reposicao',
    # Vendas
    'vendas', 'nova_venda', 'buscar_clientes', 'buscar_produtos',
    'buscar_formas_pagamento', 'criar_venda', 'gerar_pdf_venda',
    # Orçamentos
    'novo_orcamento', 'criar_orcamento', 'buscar_clientes_orcamento',
    'buscar_produtos_orcamento', 'buscar_formas_pagamento_orcamento',
]