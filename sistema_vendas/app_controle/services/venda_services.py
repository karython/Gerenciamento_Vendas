# app_controle/services/venda_services.py

from django.db import transaction
from decimal import Decimal
from ..models import Venda, Cliente, Produto, Pagamento, Estoque

class VendaService:
    
    @staticmethod
    def listar_clientes():
        """Retorna lista de clientes para autocomplete"""
        clientes = Cliente.objects.all().order_by('NOME_CLIENTE')
        return [
            {
                'id': c.idCLIENTE,
                'nome': c.NOME_CLIENTE,
                'cpf': c.CPF,
                'label': f"{c.NOME_CLIENTE} - CPF: {c.CPF}"
            }
            for c in clientes
        ]
    
    @staticmethod
    def listar_produtos():
        """Retorna lista de produtos com estoque disponível"""
        print("[VENDA SERVICE] Buscando produtos do estoque...")
        
        # Buscar apenas produtos que têm estoque
        estoques = Estoque.objects.select_related('PRODUTO_idPRODUTO').filter(QTD_DISPONIVEL__gt=0)
        
        resultado = []
        for estoque in estoques:
            produto = estoque.PRODUTO_idPRODUTO
            qtd_disponivel = estoque.QTD_DISPONIVEL
            
            resultado.append({
                'id': produto.idPRODUTO,
                'descricao': produto.DESCRICAO,
                'valor': float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0,
                'estoque': qtd_disponivel,
                'label': f"#{produto.idPRODUTO} - {produto.DESCRICAO} - R$ {produto.VLR_UNIT} (Estoque: {qtd_disponivel})"
            })
        
        print(f"[VENDA SERVICE] Encontrados {len(resultado)} produtos com estoque")
        return resultado
    
    @staticmethod
    def listar_formas_pagamento():
        """Retorna formas de pagamento disponíveis"""
        pagamentos = Pagamento.objects.all()
        return [
            {
                'id': p.idPAGAMENTO,
                'tipo': p.TP_PAGAMENTO
            }
            for p in pagamentos
        ]
    
    @staticmethod
    @transaction.atomic
    def criar_venda(dados):
        """
        Cria uma nova venda e atualiza o estoque automaticamente
        """
        print("=" * 50)
        print(f"[VENDA SERVICE] Criando venda com dados: {dados}")
        
        # Validar cliente
        try:
            cliente = Cliente.objects.get(idCLIENTE=dados['cliente_id'])
            print(f"[VENDA SERVICE] Cliente encontrado: {cliente.NOME_CLIENTE}")
        except Cliente.DoesNotExist:
            raise ValueError("Cliente não encontrado")
        
        # Validar forma de pagamento
        try:
            pagamento = Pagamento.objects.get(idPAGAMENTO=dados['forma_pagamento_id'])
            print(f"[VENDA SERVICE] Forma de pagamento: {pagamento.TP_PAGAMENTO}")
        except Pagamento.DoesNotExist:
            raise ValueError("Forma de pagamento não encontrada")
        
        # Calcular valores
        subtotal = Decimal('0.00')
        quantidade_total = 0
        
        for item in dados['itens']:
            qtd = int(item['quantidade'])
            vlr_unit = Decimal(str(item['valor_unitario']))
            subtotal += qtd * vlr_unit
            quantidade_total += qtd
        
        desconto = Decimal(str(dados.get('desconto', 0)))
        total = subtotal - desconto
        
        print(f"[VENDA SERVICE] Subtotal: R$ {subtotal}, Desconto: R$ {desconto}, Total: R$ {total}")
        
        # Criar venda
        venda = Venda.objects.create(
            CLIENTE_idCLIENTE=cliente,
            PAGAMENTO_idPAGAMENTO=pagamento,
            QTD_VENDIDA=quantidade_total,
            VLR_TOTAL=total
        )
        
        print(f"[VENDA SERVICE] Venda criada com ID: {venda.idVENDA}")
        
        # Processar cada item e atualizar estoque
        for item_dados in dados['itens']:
            produto_id = item_dados['produto_id']
            quantidade = int(item_dados['quantidade'])
            
            print(f"[VENDA SERVICE] Processando produto ID {produto_id}, quantidade: {quantidade}")
            
            # Buscar produto
            try:
                produto = Produto.objects.get(idPRODUTO=produto_id)
            except Produto.DoesNotExist:
                raise ValueError(f"Produto ID {produto_id} não encontrado")
            
            # Buscar estoque
            estoque = Estoque.objects.filter(PRODUTO_idPRODUTO=produto).first()
            
            if not estoque:
                raise ValueError(f"Produto {produto.DESCRICAO} não possui estoque cadastrado")
            
            # Validar estoque disponível
            if estoque.QTD_DISPONIVEL < quantidade:
                raise ValueError(f"Estoque insuficiente para {produto.DESCRICAO}. Disponível: {estoque.QTD_DISPONIVEL}, Solicitado: {quantidade}")
            
            # Atualizar estoque (DESCONTA a quantidade vendida)
            estoque_anterior = estoque.QTD_DISPONIVEL
            estoque.QTD_DISPONIVEL -= quantidade
            estoque.save()
            
            print(f"[VENDA SERVICE] ✅ Estoque atualizado para {produto.DESCRICAO}:")
            print(f"[VENDA SERVICE]    Anterior: {estoque_anterior} -> Atual: {estoque.QTD_DISPONIVEL}")
        
        print(f"[VENDA SERVICE] ✅ Venda #{venda.idVENDA} finalizada com sucesso!")
        print("=" * 50)
        
        return venda
    
    @staticmethod
    def listar_vendas():
        """Lista todas as vendas"""
        return Venda.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        ).order_by('-DT_VENDA')
    
    @staticmethod
    def buscar_venda(venda_id):
        """Busca uma venda específica"""
        return Venda.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        ).get(idVENDA=venda_id)