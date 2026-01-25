# app_controle/services/orcamento_services.py
from django.db import transaction
from django.db.models import Q
from ..models import Orcamento, ItemOrcamento, Cliente, Pagamento, Produto
from decimal import Decimal


class OrcamentoService:
    """Service para gerenciar orçamentos"""
    
    @staticmethod
    def criar_orcamento(dados):
        """
        Cria um novo orçamento sem dar baixa no estoque
        
        Args:
            dados (dict): Dados do orçamento contendo:
                - cliente_id: ID do cliente
                - forma_pagamento_id: ID da forma de pagamento
                - itens: Lista de itens com produto_id, quantidade, valor_unitario, valor_total
                - subtotal: Valor subtotal
                - desconto: Valor do desconto
                - total: Valor total
        
        Returns:
            Orcamento: Objeto do orçamento criado
        """
        with transaction.atomic():
            # Validar cliente
            try:
                cliente = Cliente.objects.get(idCLIENTE=dados['cliente_id'])
            except Cliente.DoesNotExist:
                raise ValueError('Cliente não encontrado')
            
            # Validar forma de pagamento
            try:
                pagamento = Pagamento.objects.get(idPAGAMENTO=dados['forma_pagamento_id'])
            except Pagamento.DoesNotExist:
                raise ValueError('Forma de pagamento não encontrada')
            
            # Validar itens
            if not dados.get('itens') or len(dados['itens']) == 0:
                raise ValueError('É necessário adicionar pelo menos um item ao orçamento')
            
            # Extrair valores
            vlr_subtotal = Decimal(str(dados.get('subtotal', 0)))
            desconto = Decimal(str(dados.get('desconto', 0)))
            vlr_total = Decimal(str(dados.get('total', 0)))
            qtd_itens = len(dados.get('itens', []))
            
            # Validar desconto
            if desconto < 0:
                raise ValueError('O desconto não pode ser negativo')
            
            if desconto > vlr_subtotal:
                raise ValueError('O desconto não pode ser maior que o subtotal')
            
            # Criar orçamento
            orcamento = Orcamento.objects.create(
                CLIENTE_idCLIENTE=cliente,
                PAGAMENTO_idPAGAMENTO=pagamento,
                QTD_ITENS=qtd_itens,
                VLR_SUBTOTAL=vlr_subtotal,
                DESCONTO=desconto,
                VLR_TOTAL=vlr_total,
                STATUS='PENDENTE'
            )
            
            print(f"[ORCAMENTO SERVICE] Orçamento #{orcamento.idORCAMENTO} criado")
            
            # Criar itens do orçamento
            for item_data in dados.get('itens', []):
                try:
                    produto = Produto.objects.get(idPRODUTO=item_data['produto_id'])
                except Produto.DoesNotExist:
                    raise ValueError(f"Produto ID {item_data['produto_id']} não encontrado")
                
                quantidade = Decimal(str(item_data['quantidade']))
                valor_unitario = Decimal(str(item_data['valor_unitario']))
                valor_total = Decimal(str(item_data['valor_total']))
                
                # Validar quantidade
                if quantidade <= 0:
                    raise ValueError(f'Quantidade inválida para o produto {produto.DESCRICAO}')
                
                # Criar item do orçamento
                ItemOrcamento.objects.create(
                    ORCAMENTO_idORCAMENTO=orcamento,
                    PRODUTO_idPRODUTO=produto,
                    QUANTIDADE=quantidade,
                    VLR_UNITARIO=valor_unitario,
                    VLR_TOTAL=valor_total
                )
                
                print(f"  ✅ Item adicionado: {produto.DESCRICAO} x{quantidade}")
            
            print(f"[ORCAMENTO SERVICE] Orçamento #{orcamento.idORCAMENTO} criado com {qtd_itens} itens")
            print(f"[ORCAMENTO SERVICE] Valor total: R$ {vlr_total}")
            
            return orcamento
    
    @staticmethod
    def listar_orcamentos(filtros=None):
        """
        Lista orçamentos com filtros opcionais
        
        Args:
            filtros (dict): Dicionário com filtros opcionais:
                - cliente_nome: Nome do cliente
                - data_inicio: Data inicial
                - data_fim: Data final
                - status: Status do orçamento
        
        Returns:
            QuerySet: Lista de orçamentos
        """
        orcamentos = Orcamento.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        ).prefetch_related('itens__PRODUTO_idPRODUTO')
        
        if not filtros:
            return orcamentos.order_by('-DT_ORCAMENTO')
        
        # Filtro por nome do cliente
        if filtros.get('cliente_nome'):
            orcamentos = orcamentos.filter(
                CLIENTE_idCLIENTE__NOME_CLIENTE__icontains=filtros['cliente_nome']
            )
        
        # Filtro por data inicial
        if filtros.get('data_inicio'):
            orcamentos = orcamentos.filter(
                DT_ORCAMENTO__date__gte=filtros['data_inicio']
            )
        
        # Filtro por data final
        if filtros.get('data_fim'):
            orcamentos = orcamentos.filter(
                DT_ORCAMENTO__date__lte=filtros['data_fim']
            )
        
        # Filtro por status
        if filtros.get('status') and filtros['status'] != 'todos':
            orcamentos = orcamentos.filter(STATUS=filtros['status'])
        
        return orcamentos.order_by('-DT_ORCAMENTO')
    
    @staticmethod
    def obter_orcamento(orcamento_id):
        """
        Obtém um orçamento específico com seus itens
        
        Args:
            orcamento_id (int): ID do orçamento
        
        Returns:
            Orcamento: Objeto do orçamento
        """
        try:
            return Orcamento.objects.select_related(
                'CLIENTE_idCLIENTE',
                'PAGAMENTO_idPAGAMENTO'
            ).prefetch_related('itens__PRODUTO_idPRODUTO').get(idORCAMENTO=orcamento_id)
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def atualizar_status(orcamento_id, novo_status):
        """
        Atualiza o status de um orçamento
        
        Args:
            orcamento_id (int): ID do orçamento
            novo_status (str): Novo status (PENDENTE, APROVADO, REJEITADO, CONVERTIDO)
        
        Returns:
            Orcamento: Objeto do orçamento atualizado
        """
        status_validos = ['PENDENTE', 'APROVADO', 'REJEITADO', 'CONVERTIDO']
        
        if novo_status not in status_validos:
            raise ValueError(f'Status inválido. Use: {", ".join(status_validos)}')
        
        try:
            orcamento = Orcamento.objects.get(idORCAMENTO=orcamento_id)
            orcamento.STATUS = novo_status
            orcamento.save()
            
            print(f"[ORCAMENTO SERVICE] Status do orçamento #{orcamento_id} atualizado para {novo_status}")
            
            return orcamento
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def deletar_orcamento(orcamento_id):
        """
        Deleta um orçamento e seus itens
        
        Args:
            orcamento_id (int): ID do orçamento
        
        Returns:
            bool: True se deletado com sucesso
        """
        try:
            orcamento = Orcamento.objects.get(idORCAMENTO=orcamento_id)
            
            # Não permitir deletar orçamentos convertidos em venda
            if orcamento.STATUS == 'CONVERTIDO':
                raise ValueError('Não é possível deletar um orçamento já convertido em venda')
            
            orcamento_numero = orcamento.idORCAMENTO
            orcamento.delete()
            
            print(f"[ORCAMENTO SERVICE] Orçamento #{orcamento_numero} deletado com sucesso")
            
            return True
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def converter_para_venda(orcamento_id):
        """
        Converte um orçamento em venda (para implementação futura)
        
        Args:
            orcamento_id (int): ID do orçamento
        
        Returns:
            dict: Dados para criar a venda
        """
        try:
            orcamento = OrcamentoService.obter_orcamento(orcamento_id)
            
            # Validar status
            if orcamento.STATUS == 'CONVERTIDO':
                raise ValueError('Este orçamento já foi convertido em venda')
            
            if orcamento.STATUS == 'REJEITADO':
                raise ValueError('Não é possível converter um orçamento rejeitado em venda')
            
            # Preparar dados para venda
            dados_venda = {
                'cliente_id': orcamento.CLIENTE_idCLIENTE.idCLIENTE,
                'forma_pagamento_id': orcamento.PAGAMENTO_idPAGAMENTO.idPAGAMENTO,
                'desconto': float(orcamento.DESCONTO),
                'itens': []
            }
            
            # Adicionar itens
            for item in orcamento.itens.all():
                dados_venda['itens'].append({
                    'produto_id': item.PRODUTO_idPRODUTO.idPRODUTO,
                    'quantidade': float(item.QUANTIDADE),
                    'valor_unitario': float(item.VLR_UNITARIO),
                    'valor_total': float(item.VLR_TOTAL)
                })
            
            return dados_venda
            
        except Orcamento.DoesNotExist:
            raise ValueError(f'Orçamento #{orcamento_id} não encontrado')
    
    @staticmethod
    def obter_estatisticas():
        """
        Obtém estatísticas dos orçamentos
        
        Returns:
            dict: Estatísticas com totais por status
        """
        from django.db.models import Count, Sum
        
        stats = Orcamento.objects.aggregate(
            total_orcamentos=Count('idORCAMENTO'),
            total_pendentes=Count('idORCAMENTO', filter=Q(STATUS='PENDENTE')),
            total_aprovados=Count('idORCAMENTO', filter=Q(STATUS='APROVADO')),
            total_rejeitados=Count('idORCAMENTO', filter=Q(STATUS='REJEITADO')),
            total_convertidos=Count('idORCAMENTO', filter=Q(STATUS='CONVERTIDO')),
            valor_total=Sum('VLR_TOTAL')
        )
        
        return {
            'total_orcamentos': stats['total_orcamentos'] or 0,
            'total_pendentes': stats['total_pendentes'] or 0,
            'total_aprovados': stats['total_aprovados'] or 0,
            'total_rejeitados': stats['total_rejeitados'] or 0,
            'total_convertidos': stats['total_convertidos'] or 0,
            'valor_total': float(stats['valor_total'] or 0)
        }