# app_controle/admin.py
"""
Configuração do Django Admin com interfaces melhoradas
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import (
    Loja, Cliente, UF, Cidade, Endereco,
    Produto, Estoque, Venda, ItemVenda,
    Orcamento, ItemOrcamento, FormaPagamento
)


# ============================================================================
# CONFIGURAÇÃO GLOBAL DO ADMIN
# ============================================================================

admin.site.site_header = 'Sistema de Controle de Vendas'
admin.site.site_title = 'Admin - Sistema de Vendas'
admin.site.index_title = 'Painel Administrativo'


# ============================================================================
# LOJA
# ============================================================================

@admin.register(Loja)
class LojaAdmin(admin.ModelAdmin):
    """Admin para Loja com campos atualizados"""
    
    list_display = [
        'id', 'nome', 'cnpj', 'telefone', 
        'email', 'ativo_icon', 'criado_em'
    ]
    list_filter = ['ativo', 'criado_em']
    search_fields = ['nome', 'cnpj', 'email']
    readonly_fields = ['senha', 'criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'cnpj', 'ativo')
        }),
        ('Contato', {
            'fields': ('telefone', 'email', 'endereco')
        }),
        ('Segurança', {
            'fields': ('senha',),
            'classes': ('collapse',),
            'description': 'Senha criptografada. Use o formulário de cadastro para alterar.'
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def ativo_icon(self, obj):
        """Ícone de status ativo"""
        if obj.ativo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ Ativo</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">❌ Inativo</span>'
        )
    ativo_icon.short_description = 'Status'


# ============================================================================
# CLIENTE
# ============================================================================

class EnderecoInline(admin.TabularInline):
    """Inline de endereços do cliente"""
    model = Endereco
    extra = 0
    fields = ['logradouro', 'numero', 'bairro', 'cep', 'cidade', 'principal']
    # ✅ REMOVIDO: readonly_fields (Endereco não tem criado_em)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin para Cliente com endereços inline"""
    
    list_display = [
        'id', 'nome', 'cpf', 'telefone', 
        'email', 'idade_display', 'total_vendas', 'criado_em'
    ]
    list_filter = ['criado_em', 'data_nascimento']
    search_fields = ['nome', 'cpf', 'telefone', 'email']
    readonly_fields = ['criado_em', 'atualizado_em', 'idade_display']
    inlines = [EnderecoInline]
    
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('nome', 'cpf', 'data_nascimento', 'idade_display')
        }),
        ('Contato', {
            'fields': ('telefone', 'email')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def idade_display(self, obj):
        """Exibe idade do cliente"""
        if obj.idade:
            return f"{obj.idade} anos"
        return "—"
    idade_display.short_description = 'Idade'
    
    def total_vendas(self, obj):
        """Quantidade de vendas do cliente"""
        total = obj.vendas.count()
        if total > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} vendas</span>',
                total
            )
        return "—"
    total_vendas.short_description = 'Total de Vendas'


# ============================================================================
# LOCALIZAÇÃO
# ============================================================================

@admin.register(UF)
class UFAdmin(admin.ModelAdmin):
    """Admin para UF"""
    
    list_display = ['id', 'sigla', 'nome', 'total_cidades']
    search_fields = ['nome', 'sigla']
    ordering = ['sigla']
    
    def total_cidades(self, obj):
        """Quantidade de cidades no estado"""
        total = obj.cidades.count()
        return f"{total} cidades"
    total_cidades.short_description = 'Total de Cidades'


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    """Admin para Cidade"""
    
    list_display = ['id', 'nome', 'uf', 'total_enderecos']
    list_filter = ['uf']
    search_fields = ['nome', 'uf__sigla', 'uf__nome']
    ordering = ['uf__sigla', 'nome']
    
    def total_enderecos(self, obj):
        """Quantidade de endereços na cidade"""
        return obj.enderecos.count()
    total_enderecos.short_description = 'Endereços'


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):
    """Admin para Endereço"""
    
    list_display = [
        'id', 'cliente', 'logradouro', 'numero', 
        'bairro', 'cidade', 'principal_icon'
    ]
    list_filter = ['principal', 'cidade__uf', 'cidade']
    search_fields = [
        'cliente__nome', 'logradouro', 'bairro', 
        'cep', 'cidade__nome'
    ]
    # ✅ REMOVIDO: readonly_fields (Endereco não tem timestamps)
    
    def principal_icon(self, obj):
        """Ícone de endereço principal"""
        if obj.principal:
            return format_html('<span style="color: gold;">⭐ Principal</span>')
        return "—"
    principal_icon.short_description = 'Principal'


# ============================================================================
# PRODUTO E ESTOQUE
# ============================================================================

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Admin para Produto"""
    
    list_display = [
        'id', 'descricao', 'preco_unitario_display', 
        'iof_display', 'controlar_estoque_icon', 
        'estoque_atual', 'criado_em'
    ]
    list_filter = ['controlar_estoque', 'criado_em']
    search_fields = ['descricao']
    readonly_fields = ['criado_em', 'atualizado_em', 'preco_com_iof']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'controlar_estoque')
        }),
        ('Precificação', {
            'fields': ('preco_unitario', 'iof', 'preco_com_iof')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def preco_unitario_display(self, obj):
        """Exibe preço formatado"""
        return f"R$ {obj.preco_unitario:.2f}"
    preco_unitario_display.short_description = 'Preço Venda'
    
    def iof_display(self, obj):
        """Exibe IOF/custo formatado"""
        if obj.iof:
            return f"R$ {obj.iof:.2f}"
        return "—"
    iof_display.short_description = 'Preço Custo'
    
    def controlar_estoque_icon(self, obj):
        """Ícone de controle de estoque"""
        if obj.controlar_estoque:
            return format_html('<span style="color: blue;">📦 Sim</span>')
        return format_html('<span style="color: gray;">🔧 Serviço</span>')
    controlar_estoque_icon.short_description = 'Controla Estoque'
    
    def estoque_atual(self, obj):
        """Exibe quantidade em estoque"""
        try:
            estoque = obj.estoque
            qtd = estoque.quantidade_disponivel
            
            if estoque.precisa_reposicao:
                return format_html(
                    '<span style="color: red; font-weight: bold;">⚠️ {}</span>',
                    qtd
                )
            return format_html('<span style="color: green;">{}</span>', qtd)
        except Estoque.DoesNotExist:
            return "—"
    estoque_atual.short_description = 'Estoque'


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    """Admin para Estoque"""
    
    list_display = [
        'id', 'produto', 'quantidade_disponivel', 
        'quantidade_minima', 'status_estoque', 'criado_em'
    ]
    list_filter = ['criado_em']
    search_fields = ['produto__descricao']
    readonly_fields = ['criado_em', 'atualizado_em', 'precisa_reposicao']
    
    fieldsets = (
        ('Produto', {
            'fields': ('produto',)
        }),
        ('Quantidades', {
            'fields': (
                'quantidade_disponivel', 
                'quantidade_minima', 
                'precisa_reposicao'
            )
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def status_estoque(self, obj):
        """Ícone de status do estoque"""
        if obj.precisa_reposicao:
            return format_html(
                '<span style="color: red; font-weight: bold;">⚠️ REPOR</span>'
            )
        return format_html(
            '<span style="color: green;">✅ OK</span>'
        )
    status_estoque.short_description = 'Status'


# ============================================================================
# FORMA DE PAGAMENTO
# ============================================================================

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    """Admin para Forma de Pagamento"""
    
    # ✅ CORRIGIDO: Removido 'criado_em' de list_display e list_filter
    list_display = ['id', 'nome', 'ativo_icon']
    list_filter = ['ativo']
    search_fields = ['nome']
    
    def ativo_icon(self, obj):
        """Ícone de status ativo"""
        if obj.ativo:
            return format_html(
                '<span style="color: green;">✅ Ativo</span>'
            )
        return format_html(
            '<span style="color: red;">❌ Inativo</span>'
        )
    ativo_icon.short_description = 'Status'


# ============================================================================
# VENDA
# ============================================================================

class ItemVendaInline(admin.TabularInline):
    """Inline de itens da venda"""
    model = ItemVenda
    extra = 0
    readonly_fields = ['produto', 'quantidade', 'preco_unitario', 'total']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Não permite adicionar itens pelo admin"""
        return False


@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    """Admin para Venda com itens inline"""
    
    list_display = [
        'id', 'cliente', 'data_venda', 
        'total_display', 'forma_pagamento', 
        'quantidade_itens_display'
    ]
    list_filter = ['data_venda', 'forma_pagamento', 'criado_em']
    search_fields = ['cliente__nome', 'cliente__cpf']
    readonly_fields = [
        'data_venda', 'subtotal', 'desconto', 
        'frete', 'total', 'criado_em', 'atualizado_em'
    ]
    date_hierarchy = 'data_venda'
    inlines = [ItemVendaInline]
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'frete', 'total')
        }),
        ('Pagamento', {
            'fields': ('forma_pagamento', 'parcelamento')
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
        ('Orçamento', {
            'fields': ('orcamento_origem',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_venda', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        """Exibe total formatado"""
        return format_html(
            '<span style="color: green; font-weight: bold;">R$ {:.2f}</span>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def quantidade_itens_display(self, obj):
        """Exibe quantidade de itens"""
        qtd = obj.quantidade_itens
        return f"{qtd} itens"
    quantidade_itens_display.short_description = 'Qtd Itens'


@admin.register(ItemVenda)
class ItemVendaAdmin(admin.ModelAdmin):
    """Admin para Item de Venda"""
    
    list_display = [
        'id', 'venda', 'produto', 
        'quantidade', 'preco_unitario_display', 'total_display'
    ]
    list_filter = ['venda__data_venda']
    search_fields = ['venda__id', 'produto__descricao']
    readonly_fields = ['total']
    
    def preco_unitario_display(self, obj):
        """Exibe preço unitário formatado"""
        return f"R$ {obj.preco_unitario:.2f}"
    preco_unitario_display.short_description = 'Preço Unit.'
    
    def total_display(self, obj):
        """Exibe total formatado"""
        return f"R$ {obj.total:.2f}"
    total_display.short_description = 'Total'


# ============================================================================
# ORÇAMENTO
# ============================================================================

class ItemOrcamentoInline(admin.TabularInline):
    """Inline de itens do orçamento"""
    model = ItemOrcamento
    extra = 0
    readonly_fields = ['produto', 'quantidade', 'preco_unitario', 'total']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Não permite adicionar itens pelo admin"""
        return False


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    """Admin para Orçamento"""
    
    list_display = [
        'id', 'cliente', 'data_orcamento', 
        'total_display', 'status_display', 'forma_pagamento'
    ]
    list_filter = ['status', 'data_orcamento', 'forma_pagamento']
    search_fields = ['cliente__nome', 'cliente__cpf']
    readonly_fields = [
        'data_orcamento', 'subtotal', 'desconto', 
        'frete', 'total', 'criado_em', 'atualizado_em'
    ]
    date_hierarchy = 'data_orcamento'
    inlines = [ItemOrcamentoInline]
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'frete', 'total')
        }),
        ('Pagamento', {
            'fields': ('forma_pagamento', 'parcelamento')
        }),
        ('Observações', {
            'fields': ('observacao',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_orcamento', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def total_display(self, obj):
        """Exibe total formatado"""
        return format_html(
            '<span style="font-weight: bold;">R$ {:.2f}</span>',
            obj.total
        )
    total_display.short_description = 'Total'
    
    def status_display(self, obj):
        """Exibe status com cores"""
        cores = {
            'PENDENTE': 'orange',
            'APROVADO': 'green',
            'REJEITADO': 'red',
            'CONVERTIDO': 'blue',
        }
        cor = cores.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            cor, obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(ItemOrcamento)
class ItemOrcamentoAdmin(admin.ModelAdmin):
    """Admin para Item de Orçamento"""
    
    list_display = [
        'id', 'orcamento', 'produto', 
        'quantidade', 'preco_unitario_display', 'total_display'
    ]
    list_filter = ['orcamento__data_orcamento', 'orcamento__status']
    search_fields = ['orcamento__id', 'produto__descricao']
    readonly_fields = ['total']
    
    def preco_unitario_display(self, obj):
        """Exibe preço unitário formatado"""
        return f"R$ {obj.preco_unitario:.2f}"
    preco_unitario_display.short_description = 'Preço Unit.'
    
    def total_display(self, obj):
        """Exibe total formatado"""
        return f"R$ {obj.total:.2f}"
    total_display.short_description = 'Total'

