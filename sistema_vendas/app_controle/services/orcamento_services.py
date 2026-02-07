# app_controle/services/orcamento_services.py
"""
Service de gerenciamento de orçamentos
"""

from django.db import transaction
from django.db.models import Q, Count, Sum
from decimal import Decimal
from ..models import Orcamento, ItemOrcamento, Cliente, FormaPagamento, Produto


class OrcamentoService:
    
    @staticmethod
    @transaction.atomic
    def criar_orcamento(dados):
        """
        Cria um novo orçamento sem dar baixa no estoque
        
        Args:
            dados (dict): Dados do orçamento
                - cliente_id (int): ID do cliente
                - forma_pagamento_id (int): ID da forma de pagamento
                - itens (list): Lista de itens
                - subtotal (Decimal): Subtotal
                - desconto (Decimal): Desconto
                - frete (Decimal): Frete
                - total (Decimal): Total
                - observacao (str, opcional): Observações
                - parcelamento (str, opcional): Parcelamento
        
        Returns:
            Orcamento: Objeto do orçamento criado
        
        Raises:
            ValueError: Se dados inválidos
        """
        # Validar cliente
        try:
            # ✅ Usar novo nome
            cliente = Cliente.objects.get(id=dados['cliente_id'])  # ✅ Novo nome
        except Cliente.DoesNotExist:
            raise ValueError('Cliente não encontrado')
        
        # Validar forma de pagamento
        try:
            # ✅ Usar novo nome
            pagamento = FormaPagamento.objects.get(id=dados['forma_pagamento_id'])  # ✅ Novo nome
        except FormaPagamento.DoesNotExist:
            raise ValueError('Forma de pagamento não encontrada')
        
        # Validar itens
        if not dados.get('itens') or len(dados['itens']) == 0:
            raise ValueError('É necessário adicionar pelo menos um item ao orçamento')
        
        # Extrair valores
        vlr_subtotal = Decimal(str(dados.get('subtotal', 0)))
        desconto = Decimal(str(dados.get('desconto', 0)))
        vlr_frete = Decimal(str(dados.get('frete', 0)))
        vlr_total = Decimal(str(dados.get('total', 0)))
        qtd_itens = len(dados.get('itens', []))
        
        # Observação
        observacao = dados.get('observacao', '')
        if observacao is None:
            observacao = ''
        if len(str(observacao)) > 3000:
            raise ValueError('Observação não pode ter mais que 3000 caracteres')
        
        # Validações
        if desconto < 0:
            raise ValueError('O desconto não pode ser negativo')
        
        if desconto > vlr_subtotal:
            raise ValueError('O desconto não pode ser maior que o subtotal')

        if vlr_frete < 0:
            raise ValueError('O valor do frete não pode ser negativo')
        
        parcelamento = dados.get('parcelamento', '')
        
        # ✅ Criar orçamento com novos nomes
        orcamento = Orcamento.objects.create(
            cliente=cliente,  # ✅ Novo nome
            forma_pagamento=pagamento,  # ✅ Novo nome
            subtotal=vlr_subtotal,  # ✅ Novo nome
            desconto=desconto,  # ✅ Novo nome
            frete=vlr_frete,  # ✅ Novo nome
            observacao=observacao,  # ✅ Novo nome
            parcelamento=parcelamento,  # ✅ Novo nome
            total=vlr_total,  # ✅ Novo nome
            status='PENDENTE'  # ✅ Novo nome
        )
        
        # Criar itens do orçamento (buscar produtos em uma query)
        produto_ids = [i['produto_id'] for i in dados.get('itens', [])]
        # ✅ Usar novos nomes
        produtos_map = {
            p.id: p for p in Produto.objects.filter(id__in=produto_ids).only(
                'id', 'descricao', 'preco_unitario'  # ✅ Novos nomes
            )
        }

        for item_data in dados.get('itens', []):
            produto = produtos_map.get(item_data['produto_id'])
            if not produto:
                raise ValueError(f"Produto ID {item_data['produto_id']} não encontrado")

            quantidade = Decimal(str(item_data['quantidade']))
            valor_unitario = Decimal(str(item_data['valor_unitario']))
            valor_total = Decimal(str(item_data['valor_total']))

            # Validar quantidade
            if quantidade <= 0:
                raise ValueError(
                    f'Quantidade inválida para o produto {produto.descricao}'  # ✅ Novo nome
                )

            # ✅ Criar item do orçamento com novos nomes
            ItemOrcamento.objects.create(
                orcamento=orcamento,  # ✅ Novo nome
                produto=produto,  # ✅ Novo nome
                quantidade=quantidade,  # ✅ Novo nome
                preco_unitario=valor_unitario,  # ✅ Novo nome
                total=valor_total  # ✅ Novo nome
            )
        
        return orcamento
    
    @staticmethod
    def listar_orcamentos(filtros=None):
        """
        Lista orçamentos com filtros opcionais
        
        Args:
            filtros (dict): Filtros opcionais
                - cliente_nome (str): Nome do cliente
                - data_inicio (str): Data inicial
                - data_fim (str): Data final
                - status (str): Status do orçamento
        
        Returns:
            QuerySet: Lista de orçamentos
        """
        # ✅ Usar novos nomes
        orcamentos = Orcamento.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        ).prefetch_related('itens__produto').only(  # ✅ Novos nomes
            'id', 'data_orcamento', 'total', 'status',  # ✅ Novos nomes
            'cliente__nome', 'forma_pagamento__nome'  # ✅ Novos nomes
        )
        
        if not filtros:
            # ✅ Ordenar por novo nome
            return orcamentos.order_by('-data_orcamento')  # ✅ Novo nome
        
        # Filtro por nome do cliente
        if filtros.get('cliente_nome'):
            # ✅ Usar novo nome
            orcamentos = orcamentos.filter(
                cliente__nome__icontains=filtros['cliente_nome']  # ✅ Novo nome
            )
        
        # Filtro por data inicial
        if filtros.get('data_inicio'):
            # ✅ Usar novo nome
            orcamentos = orcamentos.filter(
                data_orcamento__date__gte=filtros['data_inicio']  # ✅ Novo nome
            )
        
        # Filtro por data final
        if filtros.get('data_fim'):
            # ✅ Usar novo nome
            orcamentos = orcamentos.filter(
                data_orcamento__date__lte=filtros['data_fim']  # ✅ Novo nome
            )
        
        # Filtro por status
        if filtros.get('status') and filtros['status'] != 'todos':
            # ✅ Usar novo nome
            orcamentos = orcamentos.filter(status=filtros['status'])  # ✅ Novo nome
        
        # ✅ Ordenar por novo nome
        return orcamentos.order_by('-data_orcamento')  # ✅ Novo nome
    
    @staticmethod
    def obter_orcamento(orcamento_id):
        """
        Obtém um orçamento específico com seus itens
        
        Args:
            orcamento_id (int): ID do orçamento
        
        Returns:
            Orcamento: Objeto do orçamento
        
        Raises:
            ValueError: Se orçamento não encontrado
        """
        try:
            from django.db.models import Prefetch
            
            # ✅ Usar novos nomes
            itens_qs = ItemOrcamento.objects.select_related('produto').only(
                'quantidade', 'preco_unitario', 'total',  # ✅ Novos nomes
                'produto__id', 'produto__descricao'  # ✅ Novos nomes
            )
            
            return Orcamento.objects.select_related(
                'cliente',  # ✅ Novo nome
                'forma_pagamento'  # ✅ Novo nome
            ).prefetch_related(
                Prefetch('itens', queryset=itens_qs)  # ✅ Novo nome (related_name)
            ).only(
                'id', 'data_orcamento', 'total', 'desconto', 'frete', 'observacao',  # ✅ Novos nomes
                'cliente__nome', 'forma_pagamento__nome'  # ✅ Novos nomes
            ).get(id=orcamento_id)  # ✅ Novo nome
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def atualizar_status(orcamento_id, novo_status):
        """
        Atualiza o status de um orçamento
        
        Args:
            orcamento_id (int): ID do orçamento
            novo_status (str): Novo status
        
        Returns:
            Orcamento: Orçamento atualizado
        
        Raises:
            ValueError: Se status inválido ou orçamento não encontrado
        """
        status_validos = ['PENDENTE', 'APROVADO', 'REJEITADO', 'CONVERTIDO']
        
        if novo_status not in status_validos:
            raise ValueError(f'Status inválido. Use: {", ".join(status_validos)}')
        
        try:
            # ✅ Buscar e atualizar com novos nomes
            orcamento = Orcamento.objects.get(id=orcamento_id)  # ✅ Novo nome
            orcamento.status = novo_status  # ✅ Novo nome
            orcamento.save()
            
            return orcamento
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    @transaction.atomic
    def deletar_orcamento(orcamento_id):
        """
        Deleta um orçamento e seus itens
        
        Args:
            orcamento_id (int): ID do orçamento
        
        Returns:
            bool: True se deletado
        
        Raises:
            ValueError: Se orçamento já convertido ou não encontrado
        """
        try:
            # ✅ Buscar orçamento (novo nome)
            orcamento = Orcamento.objects.get(id=orcamento_id)  # ✅ Novo nome
            
            # ✅ Validar status (novo nome)
            if orcamento.status == 'CONVERTIDO':  # ✅ Novo nome
                raise ValueError('Não é possível deletar um orçamento já convertido em venda')
            
            # Deletar (CASCADE deleta itens automaticamente)
            orcamento.delete()
            
            return True
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def obter_estatisticas():
        """
        Obtém estatísticas dos orçamentos
        
        Returns:
            dict: Estatísticas com totais por status
        """
        # ✅ Usar novos nomes
        stats = Orcamento.objects.aggregate(
            total_orcamentos=Count('id'),  # ✅ Novo nome
            total_pendentes=Count('id', filter=Q(status='PENDENTE')),  # ✅ Novos nomes
            total_aprovados=Count('id', filter=Q(status='APROVADO')),  # ✅ Novos nomes
            total_rejeitados=Count('id', filter=Q(status='REJEITADO')),  # ✅ Novos nomes
            total_convertidos=Count('id', filter=Q(status='CONVERTIDO')),  # ✅ Novos nomes
            valor_total=Sum('total')  # ✅ Novo nome
        )
        
        return {
            'total_orcamentos': stats['total_orcamentos'] or 0,
            'total_pendentes': stats['total_pendentes'] or 0,
            'total_aprovados': stats['total_aprovados'] or 0,
            'total_rejeitados': stats['total_rejeitados'] or 0,
            'total_convertidos': stats['total_convertidos'] or 0,
            'valor_total': float(stats['valor_total'] or 0)
        }