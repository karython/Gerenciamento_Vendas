# app_controle/models/__init__.py
from .funcionario import Funcionario
from .cliente import Cliente
from .uf import UF
from .cidades import Cidades
from .endereco import Endereco
from .produto import Produto
from .estoque import Estoque
from .pagamento import Pagamento
from .venda import Venda
from .orcamento import Orcamento
from .item_venda import ItemVenda
from .item_orcamento import ItemOrcamento  # ← ADICIONAR ESTE IMPORT
from .estoque_venda import EstoqueVenda
from .usuario import Usuario
from .loja import Loja

__all__ = [
    'Funcionario',
    'Cliente',
    'UF',
    'Cidades',
    'Endereco',
    'Produto',
    'Estoque',
    'Pagamento',
    'Venda',
    'Orcamento',
    'ItemVenda',
    'ItemOrcamento',  # ← JÁ ESTÁ AQUI, MAS FALTAVA O IMPORT ACIMA
    'EstoqueVenda',
    'Usuario',
    'Loja',
]