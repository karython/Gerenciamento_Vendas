# app_controle/models.py
"""
Models do Sistema de Controle de Vendas
Refatorado seguindo as melhores práticas Django
"""

from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from decimal import Decimal


# ============================================================================
# MANAGERS CUSTOMIZADOS
# ============================================================================

class AtivoManager(models.Manager):
    """Manager para retornar apenas registros ativos"""
    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


# ============================================================================
# MODELS BASE
# ============================================================================

class TimeStampedModel(models.Model):
    """Model abstrato com timestamps automáticos"""
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        abstract = True


# ============================================================================
# LOCALIZAÇÃO
# ============================================================================

class UF(models.Model):
    """Estados brasileiros (UF)"""
    sigla = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='Sigla',
        validators=[RegexValidator(r'^[A-Z]{2}$', 'Sigla deve ter 2 letras maiúsculas')]
    )
    nome = models.CharField(max_length=45, verbose_name='Nome do Estado')

    class Meta:
        db_table = 'uf'
        verbose_name = 'UF'
        verbose_name_plural = 'UFs'
        ordering = ['sigla']

    def __str__(self):
        return f"{self.sigla} - {self.nome}"


class Cidade(models.Model):
    """Cidades brasileiras"""
    nome = models.CharField(max_length=100, verbose_name='Nome da Cidade')
    uf = models.ForeignKey(
        UF,
        on_delete=models.PROTECT,
        related_name='cidades',
        verbose_name='UF'
    )

    class Meta:
        db_table = 'cidade'
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['nome', 'uf'], name='idx_cidade_nome_uf'),
        ]

    def __str__(self):
        return f"{self.nome}/{self.uf.sigla}"


# ============================================================================
# LOJA (AUTENTICAÇÃO)
# ============================================================================

class Loja(TimeStampedModel):
    """
    Loja/Empresa do sistema
    Responsável pela autenticação e controle de acesso
    """
    nome = models.CharField(max_length=200, verbose_name='Nome da Loja')
    cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name='CNPJ',
        validators=[RegexValidator(
            r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
            'CNPJ inválido. Use o formato: 00.000.000/0000-00'
        )]
    )
    senha = models.CharField(max_length=255, verbose_name='Senha')
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone',
        validators=[RegexValidator(
            r'^\(\d{2}\)\s?\d{4,5}-?\d{4}$',
            'Telefone inválido. Use: (00) 00000-0000'
        )]
    )
    email = models.EmailField(
        max_length=120,
        blank=True,
        verbose_name='E-mail',
        validators=[EmailValidator()]
    )
    endereco = models.CharField(max_length=255, blank=True, verbose_name='Endereço')
    ativo = models.BooleanField(default=True, verbose_name='Ativo', db_index=True)

    # Managers
    objects = models.Manager()  # Manager padrão
    ativos = AtivoManager()     # Manager para lojas ativas

    class Meta:
        db_table = 'loja'
        verbose_name = 'Loja'
        verbose_name_plural = 'Lojas'
        indexes = [
            models.Index(fields=['cnpj', 'ativo'], name='idx_loja_cnpj_ativo'),
        ]

    def __str__(self):
        return f"{self.nome} ({self.cnpj})"

    def set_password(self, raw_password):
        """Criptografa a senha usando Django hashers"""
        self.senha = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica se a senha fornecida está correta"""
        return check_password(raw_password, self.senha)

    def save(self, *args, **kwargs):
        """Override para garantir que senha seja sempre hash"""
        # Se senha não começar com algoritmo de hash, criptografar
        if self.senha and not self.senha.startswith(('pbkdf2_', 'bcrypt', 'argon2')):
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)


# ============================================================================
# FUNCIONÁRIO
# ============================================================================

class Funcionario(TimeStampedModel):
    """Funcionários da loja"""
    nome = models.CharField(max_length=120, verbose_name='Nome Completo')
    cpf_cnpj = models.CharField(
        max_length=18,
        unique=True,
        verbose_name='CPF/CNPJ',
        validators=[RegexValidator(
            r'^(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})$',
            'CPF/CNPJ inválido'
        )]
    )
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    ativo = models.BooleanField(default=True, verbose_name='Ativo', db_index=True)

    # Managers
    objects = models.Manager()
    ativos = AtivoManager()

    class Meta:
        db_table = 'funcionario'
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']

    def __str__(self):
        return self.nome


# ============================================================================
# CLIENTE
# ============================================================================

class Cliente(TimeStampedModel):
    """Clientes do sistema"""
    nome = models.CharField(max_length=120, verbose_name='Nome Completo')
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Data de Nascimento'
    )
    cpf = models.CharField(
        max_length=14,
        unique=True,
        verbose_name='CPF',
        validators=[RegexValidator(
            r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
            'CPF inválido. Use o formato: 000.000.000-00'
        )]
    )
    telefone = models.CharField(max_length=20, verbose_name='Telefone')
    email = models.EmailField(
        max_length=120,
        blank=True,
        verbose_name='E-mail',
        validators=[EmailValidator()]
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clientes',
        verbose_name='Funcionário Responsável'
    )

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['cpf'], name='idx_cliente_cpf'),
            models.Index(fields=['nome'], name='idx_cliente_nome'),
        ]

    def __str__(self):
        return self.nome

    @property
    def idade(self):
        """Calcula idade do cliente"""
        if self.data_nascimento:
            hoje = timezone.now().date()
            return hoje.year - self.data_nascimento.year - (
                (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None


# ============================================================================
# ENDEREÇO
# ============================================================================

class Endereco(models.Model):
    """Endereços dos clientes"""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='enderecos',
        verbose_name='Cliente'
    )
    logradouro = models.CharField(max_length=200, verbose_name='Logradouro')
    numero = models.CharField(max_length=20, blank=True, verbose_name='Número')
    complemento = models.CharField(max_length=100, blank=True, verbose_name='Complemento')
    bairro = models.CharField(max_length=100, blank=True, verbose_name='Bairro')
    cep = models.CharField(
        max_length=9,
        blank=True,
        verbose_name='CEP',
        validators=[RegexValidator(
            r'^\d{5}-\d{3}$',
            'CEP inválido. Use o formato: 00000-000'
        )]
    )
    cidade = models.ForeignKey(
        Cidade,
        on_delete=models.PROTECT,
        related_name='enderecos',
        verbose_name='Cidade'
    )
    principal = models.BooleanField(default=False, verbose_name='Endereço Principal')

    class Meta:
        db_table = 'endereco'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f"{self.logradouro}, {self.numero or 'S/N'} - {self.cidade}"

    def save(self, *args, **kwargs):
        """Garante que apenas um endereço seja principal por cliente"""
        if self.principal:
            Endereco.objects.filter(
                cliente=self.cliente,
                principal=True
            ).update(principal=False)
        super().save(*args, **kwargs)


# ============================================================================
# PRODUTO E ESTOQUE
# ============================================================================

class Produto(TimeStampedModel):
    """Produtos disponíveis para venda"""
    descricao = models.CharField(max_length=120, verbose_name='Descrição')
    preco_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço Unitário'
    )
    iof = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='IOF (%)'
    )
    controlar_estoque = models.BooleanField(
        default=True,
        verbose_name='Controlar Estoque'
    )
    ativo = models.BooleanField(default=True, verbose_name='Ativo', db_index=True)

    # Managers
    objects = models.Manager()
    ativos = AtivoManager()

    class Meta:
        db_table = 'produto'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['descricao']
        indexes = [
            models.Index(fields=['descricao'], name='idx_produto_descricao'),
        ]

    def __str__(self):
        return f"{self.descricao} - R$ {self.preco_unitario}"

    @property
    def preco_com_iof(self):
        """Calcula preço unitário com IOF"""
        return self.preco_unitario * (1 + self.iof / 100)


class Estoque(TimeStampedModel):
    """Controle de estoque dos produtos"""
    produto = models.OneToOneField(
        Produto,
        on_delete=models.CASCADE,
        related_name='estoque',
        verbose_name='Produto'
    )
    quantidade_disponivel = models.IntegerField(
        default=0,
        verbose_name='Quantidade Disponível'
    )
    quantidade_minima = models.IntegerField(
        default=0,
        verbose_name='Estoque Mínimo'
    )

    class Meta:
        db_table = 'estoque'
        verbose_name = 'Estoque'
        verbose_name_plural = 'Estoques'

    def __str__(self):
        return f"{self.produto.descricao}: {self.quantidade_disponivel} un."

    @property
    def precisa_reposicao(self):
        """Verifica se estoque está abaixo do mínimo"""
        return self.quantidade_disponivel <= self.quantidade_minima

    def adicionar(self, quantidade):
        """Adiciona quantidade ao estoque"""
        self.quantidade_disponivel += quantidade
        self.save()

    def remover(self, quantidade):
        """Remove quantidade do estoque (com validação)"""
        if quantidade > self.quantidade_disponivel:
            raise ValueError(
                f'Quantidade insuficiente em estoque. '
                f'Disponível: {self.quantidade_disponivel}, '
                f'Solicitado: {quantidade}'
            )
        self.quantidade_disponivel -= quantidade
        self.save()


# ============================================================================
# PAGAMENTO
# ============================================================================

class FormaPagamento(models.Model):
    """Formas de pagamento aceitas"""
    nome = models.CharField(max_length=45, unique=True, verbose_name='Nome')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    # Managers
    objects = models.Manager()
    ativos = AtivoManager()

    class Meta:
        db_table = 'forma_pagamento'
        verbose_name = 'Forma de Pagamento'
        verbose_name_plural = 'Formas de Pagamento'
        ordering = ['nome']

    def __str__(self):
        return self.nome


# ============================================================================
# ORÇAMENTO
# ============================================================================

class Orcamento(TimeStampedModel):
    """Orçamentos de vendas"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('CONVERTIDO', 'Convertido em Venda'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='orcamentos',
        verbose_name='Cliente'
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        related_name='orcamentos',
        verbose_name='Forma de Pagamento'
    )
    data_orcamento = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data do Orçamento'
    )
    
    # Valores
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Desconto'
    )
    frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Frete'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Total'
    )
    
    # Outros
    parcelamento = models.CharField(
        max_length=45,
        blank=True,
        verbose_name='Parcelamento'
    )
    observacao = models.TextField(
        max_length=3000,
        blank=True,
        verbose_name='Observação'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
        verbose_name='Status',
        db_index=True
    )

    class Meta:
        db_table = 'orcamento'
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
        ordering = ['-data_orcamento']
        indexes = [
            models.Index(fields=['status', 'data_orcamento'], name='idx_orcamento_status_data'),
        ]

    def __str__(self):
        return f"Orçamento #{self.pk} - {self.cliente.nome}"

    @property
    def quantidade_itens(self):
        """Retorna quantidade total de itens"""
        return self.itens.aggregate(
            total=models.Sum('quantidade')
        )['total'] or 0

    def calcular_total(self):
        """Calcula e atualiza o valor total"""
        self.total = self.subtotal - self.desconto + self.frete
        return self.total


class ItemOrcamento(models.Model):
    """Itens de um orçamento"""
    orcamento = models.ForeignKey(
        Orcamento,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Orçamento'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_orcamento',
        verbose_name='Produto'
    )
    quantidade = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Quantidade'
    )
    preco_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço Unitário'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total'
    )

    class Meta:
        db_table = 'item_orcamento'
        verbose_name = 'Item de Orçamento'
        verbose_name_plural = 'Itens de Orçamento'

    def __str__(self):
        return f"{self.produto.descricao} x {self.quantidade}"

    def save(self, *args, **kwargs):
        """Calcula total automaticamente"""
        self.total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)


# ============================================================================
# VENDA
# ============================================================================

class Venda(TimeStampedModel):
    """Vendas realizadas"""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='vendas',
        verbose_name='Cliente'
    )
    forma_pagamento = models.ForeignKey(
        FormaPagamento,
        on_delete=models.PROTECT,
        related_name='vendas',
        verbose_name='Forma de Pagamento'
    )
    orcamento_origem = models.OneToOneField(
        Orcamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='venda_convertida',
        verbose_name='Orçamento de Origem'
    )
    data_venda = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data da Venda'
    )
    
    # Valores
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Subtotal'
    )
    desconto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Desconto'
    )
    frete = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Frete'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Valor Total'
    )
    
    # Outros
    parcelamento = models.CharField(
        max_length=45,
        blank=True,
        verbose_name='Parcelamento'
    )
    observacao = models.TextField(
        max_length=3000,
        blank=True,
        verbose_name='Observação'
    )

    class Meta:
        db_table = 'venda'
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
        ordering = ['-data_venda']
        indexes = [
            models.Index(fields=['data_venda'], name='idx_venda_data'),
            models.Index(fields=['cliente', 'data_venda'], name='idx_venda_cliente_data'),
        ]

    def __str__(self):
        return f"Venda #{self.pk} - {self.cliente.nome}"

    @property
    def quantidade_vendida(self):
        """Retorna quantidade total de itens vendidos"""
        return self.itens.aggregate(
            total=models.Sum('quantidade')
        )['total'] or 0

    def calcular_total(self):
        """Calcula e atualiza o valor total"""
        self.total = self.subtotal - self.desconto + self.frete
        return self.total


class ItemVenda(models.Model):
    """Itens de uma venda"""
    venda = models.ForeignKey(
        Venda,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Venda'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_venda',
        verbose_name='Produto'
    )
    quantidade = models.IntegerField(verbose_name='Quantidade')
    preco_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Preço Unitário'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total'
    )

    class Meta:
        db_table = 'item_venda'
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'

    def __str__(self):
        return f"{self.produto.descricao} x {self.quantidade}"

    def save(self, *args, **kwargs):
        """Calcula total e atualiza estoque automaticamente"""
        self.total = self.quantidade * self.preco_unitario
        
        # Se é um novo item, reduzir estoque
        if not self.pk and self.produto.controlar_estoque:
            try:
                self.produto.estoque.remover(self.quantidade)
            except ValueError as e:
                raise ValueError(f"Erro ao processar estoque: {str(e)}")
        
        super().save(*args, **kwargs)


# ============================================================================
# USUÁRIO (PARA FUTURO)
# ============================================================================

class Usuario(TimeStampedModel):
    """
    Model de usuário para futuras expansões
    TODO: Migrar para AbstractUser do Django
    """
    nome = models.CharField(max_length=120, verbose_name='Nome')
    email = models.EmailField(
        max_length=120,
        unique=True,
        verbose_name='E-mail'
    )
    senha = models.CharField(max_length=255, verbose_name='Senha')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome