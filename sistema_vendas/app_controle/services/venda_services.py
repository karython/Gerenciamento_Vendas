# app_controle/services/venda_services.py

from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from datetime import datetime, timedelta
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
        
        resultado = []

        # Produtos com estoque físico
        estoques = Estoque.objects.select_related('PRODUTO_idPRODUTO').filter(QTD_DISPONIVEL__gt=0)
        produtos_incluidos = set()
        for estoque in estoques:
            produto = estoque.PRODUTO_idPRODUTO
            qtd_disponivel = estoque.QTD_DISPONIVEL
            produtos_incluidos.add(produto.idPRODUTO)

            resultado.append({
                'id': produto.idPRODUTO,
                'descricao': produto.DESCRICAO,
                'valor': float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0,
                'estoque': qtd_disponivel,
                'is_service': False,
                'label': f"#{produto.idPRODUTO} - {produto.DESCRICAO} - R$ {produto.VLR_UNIT} (Estoque: {qtd_disponivel})"
            })

        # Produtos marcados como serviço (sem controle de estoque)
        servicos = Produto.objects.filter(TRACK_STOCK=False)
        for produto in servicos:
            if produto.idPRODUTO in produtos_incluidos:
                continue
            resultado.append({
                'id': produto.idPRODUTO,
                'descricao': produto.DESCRICAO,
                'valor': float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0,
                # For services we expose is_service=True; frontend will allow any quantity
                'estoque': 1,
                'is_service': True,
                'label': f"#{produto.idPRODUTO} - {produto.DESCRICAO} - R$ {produto.VLR_UNIT} (Serviço)"
            })

        print(f"[VENDA SERVICE] Encontrados {len(resultado)} produtos/serviços")
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
        """Cria uma nova venda e atualiza o estoque automaticamente"""
        print("=" * 50)
        print(f"[VENDA SERVICE] Criando venda com dados: {dados}")
        
        try:
            cliente = Cliente.objects.get(idCLIENTE=dados['cliente_id'])
            print(f"[VENDA SERVICE] Cliente encontrado: {cliente.NOME_CLIENTE}")
        except Cliente.DoesNotExist:
            raise ValueError("Cliente não encontrado")
        
        try:
            pagamento = Pagamento.objects.get(idPAGAMENTO=dados['forma_pagamento_id'])
            print(f"[VENDA SERVICE] Forma de pagamento: {pagamento.TP_PAGAMENTO}")
        except Pagamento.DoesNotExist:
            raise ValueError("Forma de pagamento não encontrada")
        
        subtotal = Decimal('0.00')
        quantidade_total = 0
        
        for item in dados['itens']:
            qtd = int(item['quantidade'])
            vlr_unit = Decimal(str(item['valor_unitario']))
            subtotal += qtd * vlr_unit
            quantidade_total += qtd
        
        desconto = Decimal(str(dados.get('desconto', 0)))
        frete = Decimal(str(dados.get('frete', 0)))
        if frete < 0:
            raise ValueError('O valor do frete não pode ser negativo')

        # Observação (opcional) - validar tamanho
        observacao = dados.get('observacao', '')
        if observacao is None:
            observacao = ''
        if len(str(observacao)) > 3000:
            raise ValueError('O campo de observação não pode ter mais que 3000 caracteres')

        total = subtotal - desconto + frete
        
        print(f"[VENDA SERVICE] Subtotal: R$ {subtotal}, Desconto: R$ {desconto}, Total: R$ {total}")
        
        parcelamento = dados.get('parcelamento', '')
        
        venda = Venda.objects.create(
            CLIENTE_idCLIENTE=cliente,
            PAGAMENTO_idPAGAMENTO=pagamento,
            QTD_VENDIDA=quantidade_total,
            VLR_SUBTOTAL=subtotal,
            DESCONTO=desconto,
            VLR_FRETE=frete,
            OBSERVACAO=observacao,
            PARCELAMENTO=parcelamento,
            VLR_TOTAL=total
        )
        
        print(f"[VENDA SERVICE] Venda criada com ID: {venda.idVENDA}")
        
        for item_dados in dados['itens']:
            produto_id = item_dados['produto_id']
            quantidade = int(item_dados['quantidade'])
            
            print(f"[VENDA SERVICE] Processando produto ID {produto_id}, quantidade: {quantidade}")
            
            try:
                produto = Produto.objects.get(idPRODUTO=produto_id)
            except Produto.DoesNotExist:
                raise ValueError(f"Produto ID {produto_id} não encontrado")
            
            # Se o produto é controlado por estoque, validar e debitar
            if getattr(produto, 'TRACK_STOCK', True):
                estoque = Estoque.objects.filter(PRODUTO_idPRODUTO=produto).first()
                if not estoque:
                    raise ValueError(f"Produto {produto.DESCRICAO} não possui estoque cadastrado")
                if estoque.QTD_DISPONIVEL < quantidade:
                    raise ValueError(f"Estoque insuficiente para {produto.DESCRICAO}. Disponível: {estoque.QTD_DISPONIVEL}, Solicitado: {quantidade}")

                estoque_anterior = estoque.QTD_DISPONIVEL
                estoque.QTD_DISPONIVEL -= quantidade
                estoque.save()
            else:
                # Serviços: não alterar estoque físico
                estoque = None
                estoque_anterior = None
            
            # Criar ItemVenda
            valor_unitario = Decimal(str(item_dados.get('valor_unitario', 0)))
            valor_total = Decimal(str(item_dados.get('valor_total', quantidade * float(valor_unitario))))
            from ..models import ItemVenda
            ItemVenda.objects.create(
                VENDA_idVENDA=venda,
                PRODUTO_idPRODUTO=produto,
                QUANTIDADE=quantidade,
                VLR_UNITARIO=valor_unitario,
                VLR_TOTAL=valor_total
            )

            if estoque is not None:
                print(f"[VENDA SERVICE] ✅ Estoque atualizado para {produto.DESCRICAO}:")
                print(f"[VENDA SERVICE]    Anterior: {estoque_anterior} -> Atual: {estoque.QTD_DISPONIVEL}")
            else:
                print(f"[VENDA SERVICE] ℹ️ Produto '{produto.DESCRICAO}' é um serviço; estoque não alterado")
            print(f"[VENDA SERVICE] ✅ ItemVenda criado para {produto.DESCRICAO}")
        
        print(f"[VENDA SERVICE] ✅ Venda #{venda.idVENDA} finalizada com sucesso!")
        print("=" * 50)
        
        return venda
    
    @staticmethod
    def listar_vendas(data_inicio=None, data_fim=None, busca_nome=None):
        """
        Lista todas as vendas com filtros opcionais
        
        Args:
            data_inicio: String no formato 'YYYY-MM-DD' ou None
            data_fim: String no formato 'YYYY-MM-DD' ou None
            busca_nome: String para buscar pelo nome do cliente ou None
        """
        vendas = Venda.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        )
        
        # Filtro por nome do cliente
        if busca_nome:
            vendas = vendas.filter(
                Q(CLIENTE_idCLIENTE__NOME_CLIENTE__icontains=busca_nome) |
                Q(CLIENTE_idCLIENTE__CPF__icontains=busca_nome)
            )
            print(f"[VENDA SERVICE] Filtro aplicado: busca por '{busca_nome}'")
        
        # Filtro por data início
        if data_inicio:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
                vendas = vendas.filter(DT_VENDA__gte=data_inicio_dt)
                print(f"[VENDA SERVICE] Filtro aplicado: data >= {data_inicio}")
            except ValueError:
                print(f"[VENDA SERVICE] ⚠️ Data início inválida: {data_inicio}")
        
        # Filtro por data fim
        if data_fim:
            try:
                data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d')
                data_fim_dt = data_fim_dt + timedelta(days=1)
                vendas = vendas.filter(DT_VENDA__lt=data_fim_dt)
                print(f"[VENDA SERVICE] Filtro aplicado: data <= {data_fim}")
            except ValueError:
                print(f"[VENDA SERVICE] ⚠️ Data fim inválida: {data_fim}")
        
        return vendas.order_by('-DT_VENDA')
    
    @staticmethod
    def buscar_venda(venda_id):
        """Busca uma venda específica"""
        return Venda.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        ).prefetch_related('itens__PRODUTO_idPRODUTO').get(idVENDA=venda_id)
    
    @staticmethod
    @transaction.atomic
    def deletar_venda(venda_id):
        """
        Deleta uma venda e devolve os produtos ao estoque
        
        Args:
            venda_id: ID da venda a ser deletada
            
        Returns:
            str: ID formatado da venda deletada
            
        Raises:
            ValueError: Se a venda não for encontrada
        """
        print("=" * 50)
        print(f"[VENDA SERVICE] Iniciando exclusão da venda ID: {venda_id}")
        
        try:
            venda = Venda.objects.select_related(
                'CLIENTE_idCLIENTE',
                'PAGAMENTO_idPAGAMENTO'
            ).get(idVENDA=venda_id)
            
            venda_id_formatado = f"V-{venda.idVENDA:05d}"
            cliente_nome = venda.CLIENTE_idCLIENTE.NOME_CLIENTE
            
            print(f"[VENDA SERVICE] Venda encontrada: {venda_id_formatado}")
            print(f"[VENDA SERVICE] Cliente: {cliente_nome}")
            print(f"[VENDA SERVICE] Quantidade vendida: {venda.QTD_VENDIDA}")
            print(f"[VENDA SERVICE] Valor total: R$ {venda.VLR_TOTAL}")
            
            # IMPORTANTE: Aqui você precisaria devolver os produtos ao estoque
            # Como não temos a tabela de itens da venda, vamos apenas deletar
            # Se você tiver uma tabela de itens, adicione a lógica de devolução aqui
            
            print(f"[VENDA SERVICE] ⚠️ ATENÇÃO: Produtos não serão devolvidos ao estoque")
            print(f"[VENDA SERVICE] (Necessário ter tabela de itens da venda para isso)")
            
            # Deletar a venda
            venda.delete()
            
            print(f"[VENDA SERVICE] ✅ Venda {venda_id_formatado} deletada com sucesso!")
            print("=" * 50)
            
            return venda_id_formatado
            
        except Venda.DoesNotExist:
            print(f"[VENDA SERVICE] ❌ Venda ID {venda_id} não encontrada")
            raise ValueError(f"Venda não encontrada")