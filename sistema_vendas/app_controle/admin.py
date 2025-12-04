# app_controle/admin.py
from django.contrib import admin
from .models import (
    Funcionario, Cliente, UF, Cidades, Endereco,
    Produto, Estoque, Venda, Pagamento, EstoqueVenda, Usuario
)

@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['idFUNCIONARIO', 'NOME_FUNCIONARIO', 'CPF_CNPJ', 'ATIVO']
    list_filter = ['ATIVO']
    search_fields = ['NOME_FUNCIONARIO', 'CPF_CNPJ']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['idCLIENTE', 'NOME_CLIENTE', 'CPF', 'TELEFONE', 'FUNCIONARIO_idFUNCIONARIO']
    search_fields = ['NOME_CLIENTE', 'CPF']
    list_filter = ['FUNCIONARIO_idFUNCIONARIO']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['idPRODUTO', 'DESCRICAO', 'VLR_UNIT', 'DT_MOVIMENTADA']
    search_fields = ['DESCRICAO']

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['idVENDA', 'CLIENTE_idCLIENTE', 'DT_VENDA', 'VLR_TOTAL']
    list_filter = ['DT_VENDA']
    date_hierarchy = 'DT_VENDA'

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ['idESTOQUE', 'PRODUTO_idPRODUTO', 'QTD_DISPONIVEL']

# Registrar os demais
admin.site.register(UF)
admin.site.register(Cidades)
admin.site.register(Endereco)
admin.site.register(Pagamento)
admin.site.register(EstoqueVenda)
admin.site.register(Usuario)