# app_controle/services/venda_services.py
"""
Service de gerenciamento de vendas
"""

from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from datetime import datetime, timedelta
from ..models import Venda, ItemVenda, Cliente, Produto, FormaPagamento, Estoque


class VendaService:
    
    @staticmethod
    def listar_clientes():
        """
        Retorna lista de clientes para autocomplete
        
        Returns:
            list: Lista de dicts com id, nome, cpf, label
        """
        # ✅ Usar novos nomes
        clientes_qs = Cliente.objects.order_by('nome').values(
            'id', 'nome', 'cpf'  # ✅ Novos nomes
        )
        
        resultado = []
        for c in clientes_qs:
            nome = c.get('nome')
            cpf = c.get('cpf')
            resultado.append({
                'id': c.get('id'),
                'nome': nome,
                'cpf': cpf,
                'label': f"{nome} - CPF: {cpf}"
            })
        return resultado
    
    @staticmethod
    def listar_produtos():
        """
        Retorna lista de produtos com estoque disponível
        
        Returns:
            list: Lista de dicts com informações dos produtos
        """
        resultado = []

        # ✅ Produtos com estoque físico (novos nomes)
        estoques = Estoque.objects.select_related('produto').filter(
            quantidade_disponivel__gt=0  # ✅ Novo nome
        )
        produtos_incluidos = set()
        
        for estoque in estoques.iterator():
            produto = estoque.produto  # ✅ Novo nome
            qtd_disponivel = estoque.quantidade_disponivel  # ✅ Novo nome
            produtos_incluidos.add(produto.id)  # ✅ Novo nome

            resultado.append({
                'id': produto.id,  # ✅ Novo nome
                'descricao': produto.descricao,  # ✅ Novo nome
                'valor': float(produto.preco_unitario),  # ✅ Novo nome
                'estoque': qtd_disponivel,
                'is_service': False,
                'label': (
                    f"#{produto.id} - {produto.descricao} - "  # ✅ Novos nomes
                    f"R$ {produto.preco_unitario} (Estoque: {qtd_disponivel})"
                )
            })

        # ✅ Produtos marcados como serviço (novos nomes)
        servicos = Produto.objects.filter(
            controlar_estoque=False  # ✅ Novo nome
        ).only('id', 'descricao', 'preco_unitario')  # ✅ Novos nomes
        
        for produto in servicos.iterator():
            if produto.id in produtos_incluidos:  # ✅ Novo nome
                continue
            
            resultado.append({
                'id': produto.id,  # ✅ Novo nome
                'descricao': produto.descricao,  # ✅ Novo nome
                'valor': float(produto.preco_unitario),  # ✅ Novo nome
                'estoque': 1,  # Serviços sempre disponíveis
                'is_service': True,
                'label': (
                    f"#{produto.id} - {produto.descricao} - "  # ✅ Novos nomes
                    f"R$ {produto.preco_unitario} (Serviço)"
                )
            })

        return resultado
    
    @staticmethod
    def listar_formas_pagamento():
        """
        Retorna formas de pagamento disponíveis
        
        Returns:
            list: Lista de dicts com id e tipo
        """
        # ✅ Usar novos nomes
        pagamentos_qs = FormaPagamento.ativos.values('id', 'nome')  # ✅ Novos nomes
        return [
            {'id': p['id'], 'tipo': p['nome']}  # ✅ Novo nome
            for p in pagamentos_qs
        ]
    
    @staticmethod
    @transaction.atomic
    def criar_venda(dados):
        """
        Cria uma nova venda e atualiza o estoque automaticamente
        
        Args:
            dados (dict): Dados da venda
                - cliente_id (int): ID do cliente
                - forma_pagamento_id (int): ID da forma de pagamento
                - itens (list): Lista de itens da venda
                - subtotal (Decimal): Subtotal
                - desconto (Decimal): Desconto
                - frete (Decimal): Frete
                - total (Decimal): Total
                - observacao (str, opcional): Observações
                - parcelamento (str, opcional): Parcelamento
        
        Returns:
            Venda: Objeto da venda criada
        
        Raises:
            ValueError: Se dados inválidos ou estoque insuficiente
        """
        # Validar cliente
        try:
            # ✅ Usar novo nome
            cliente = Cliente.objects.get(id=dados['cliente_id'])  # ✅ Novo nome
        except Cliente.DoesNotExist:
            raise ValueError("Cliente não encontrado")
        
        # Validar forma de pagamento
        try:
            # ✅ Usar novo nome
            pagamento = FormaPagamento.objects.get(id=dados['forma_pagamento_id'])  # ✅ Novo nome
        except FormaPagamento.DoesNotExist:
            raise ValueError("Forma de pagamento não encontrada")
        
        # Calcular totais
        subtotal = Decimal('0.00')
        quantidade_total = 0
        
        for item in dados['itens']:
            qtd = int(item['quantidade'])
            vlr_unit = Decimal(str(item['valor_unitario']))
            subtotal += qtd * vlr_unit
            quantidade_total += qtd
        
        desconto = Decimal(str(dados.get('desconto', 0)))
        frete = Decimal(str(dados.get('frete', 0)))
        
        # Validações
        if frete < 0:
            raise ValueError('O valor do frete não pode ser negativo')
        
        if desconto < 0:
            raise ValueError('O desconto não pode ser negativo')
        
        if desconto > subtotal:
            raise ValueError('O desconto não pode ser maior que o subtotal')

        # Observação
        observacao = dados.get('observacao', '')
        if observacao is None:
            observacao = ''
        if len(str(observacao)) > 3000:
            raise ValueError('Observação não pode ter mais que 3000 caracteres')

        total = subtotal - desconto + frete
        parcelamento = dados.get('parcelamento', '')
        
        # ✅ Criar venda com novos nomes
        venda = Venda.objects.create(
            cliente=cliente,  # ✅ Novo nome
            forma_pagamento=pagamento,  # ✅ Novo nome
            subtotal=subtotal,  # ✅ Novo nome
            desconto=desconto,  # ✅ Novo nome
            frete=frete,  # ✅ Novo nome
            observacao=observacao,  # ✅ Novo nome
            parcelamento=parcelamento,  # ✅ Novo nome
            total=total  # ✅ Novo nome
        )
        
        # Processar itens da venda
        for item_dados in dados['itens']:
            produto_id = item_dados['produto_id']
            quantidade = int(item_dados['quantidade'])
            
            try:
                # ✅ Buscar produto (novo nome)
                produto = Produto.objects.get(id=produto_id)  # ✅ Novo nome
            except Produto.DoesNotExist:
                raise ValueError(f"Produto ID {produto_id} não encontrado")
            
            # ✅ Se o produto é controlado por estoque, validar e debitar (novo nome)
            if produto.controlar_estoque:  # ✅ Novo nome
                estoque = Estoque.objects.filter(produto=produto).first()  # ✅ Novo nome
                
                if not estoque:
                    raise ValueError(
                        f"Produto {produto.descricao} não possui estoque cadastrado"  # ✅ Novo nome
                    )
                
                # ✅ Validar quantidade (novo nome)
                if estoque.quantidade_disponivel < quantidade:  # ✅ Novo nome
                    raise ValueError(
                        f"Estoque insuficiente para {produto.descricao}. "  # ✅ Novo nome
                        f"Disponível: {estoque.quantidade_disponivel}, "  # ✅ Novo nome
                        f"Solicitado: {quantidade}"
                    )

                # ✅ Usar método do model para remover estoque
                estoque.remover(quantidade)
            
            # ✅ Criar ItemVenda com novos nomes
            valor_unitario = Decimal(str(item_dados.get('valor_unitario', 0)))
            valor_total = Decimal(str(item_dados.get('valor_total', quantidade * float(valor_unitario))))
            
            ItemVenda.objects.create(
                venda=venda,  # ✅ Novo nome
                produto=produto,  # ✅ Novo nome
                quantidade=quantidade,  # ✅ Novo nome
                preco_unitario=valor_unitario,  # ✅ Novo nome
                total=valor_total  # ✅ Novo nome
            )
        
        return venda
    
    @staticmethod
    def listar_vendas(data_inicio=None, data_fim=None, busca_nome=None):
        """
        Lista todas as vendas com filtros opcionais
        
        Args:
            data_inicio (str): Data inicial (YYYY-MM-DD)
            data_fim (str): Data final (YYYY-MM-DD)
            busca_nome (str): Nome ou CPF do cliente
        
        Returns:
            QuerySet: Vendas ordenadas por data decrescente
        """
        # ✅ Usar novos nomes
        vendas = Venda.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        )
        
        # Filtro por nome do cliente
        if busca_nome:
            # ✅ Usar novos nomes
            vendas = vendas.filter(
                Q(cliente__nome__icontains=busca_nome) |  # ✅ Novo nome
                Q(cliente__cpf__icontains=busca_nome)  # ✅ Novo nome
            )
        
        # Filtro por data início
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                # ✅ Usar novo nome
                vendas = vendas.filter(data_venda__gte=data_inicio_dt)  # ✅ Novo nome
            except ValueError:
                pass
        
        # Filtro por data fim
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_dt = data_fim_dt + timedelta(days=1)
                # ✅ Usar novo nome
                vendas = vendas.filter(data_venda__lt=data_fim_dt)  # ✅ Novo nome
            except ValueError:
                pass
        
        # ✅ Ordenar por novo nome
        return vendas.order_by('-data_venda')  # ✅ Novo nome
    
    @staticmethod
    def buscar_venda(venda_id):
        """
        Busca uma venda específica
        
        Args:
            venda_id (int): ID da venda
        
        Returns:
            Venda: Objeto da venda
        """
        # ✅ Usar novos nomes
        return Venda.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        ).prefetch_related('itens__produto').get(id=venda_id)  # ✅ Novos nomes
    
    @staticmethod
    @transaction.atomic
    def deletar_venda(venda_id):
        """
        Deleta uma venda e devolve os produtos ao estoque
        
        Args:
            venda_id (int): ID da venda
        
        Returns:
            str: ID formatado da venda deletada
        
        Raises:
            ValueError: Se venda não encontrada
        """
        try:
            # ✅ Buscar venda (novos nomes)
            venda = Venda.objects.select_related(
                'cliente',  # ✅ Novo nome
                'forma_pagamento'  # ✅ Novo nome
            ).prefetch_related('itens__produto').get(id=venda_id)  # ✅ Novos nomes
            
            # ✅ Formatar ID (novo nome)
            venda_id_formatado = f"V-{venda.id:05d}"  # ✅ Novo nome
            cliente_nome = venda.cliente.nome  # ✅ Novo nome
            
            # ✅ Devolver produtos ao estoque (novos nomes)
            for item in venda.itens.all():  # ✅ Novo nome (related_name)
                produto = item.produto  # ✅ Novo nome
                quantidade = item.quantidade  # ✅ Novo nome
                
                # ✅ Só devolver se o produto controla estoque (novo nome)
                if produto.controlar_estoque:  # ✅ Novo nome
                    estoque = Estoque.objects.filter(produto=produto).first()  # ✅ Novo nome
                    
                    if estoque:
                        # ✅ Usar método do model
                        estoque.adicionar(quantidade)
            
            # Deletar venda (CASCADE deleta itens automaticamente)
            venda.delete()
            
            return venda_id_formatado
            
        except Venda.DoesNotExist:
            raise ValueError("Venda não encontrada")