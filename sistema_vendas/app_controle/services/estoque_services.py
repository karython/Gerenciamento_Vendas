# app_controle/services/estoque_services.py

from django.db import transaction
from decimal import Decimal
from ..models import Estoque, Produto

class EstoqueService:
    
    @staticmethod
    def listar_estoque():
        """Lista todos os produtos com informações de estoque"""
        estoques = Estoque.objects.select_related('PRODUTO_idPRODUTO').only(
            'idESTOQUE', 'QTD_DISPONIVEL',
            'PRODUTO_idPRODUTO__idPRODUTO', 'PRODUTO_idPRODUTO__DESCRICAO', 'PRODUTO_idPRODUTO__IOF', 'PRODUTO_idPRODUTO__VLR_UNIT'
        )
        
        resultado = []
        for estoque in estoques.iterator():
            produto = estoque.PRODUTO_idPRODUTO
            
            # IOF armazena o preço de custo, VLR_UNIT o preço de venda
            preco_custo = float(produto.IOF) if produto.IOF and produto.IOF != '0' else 0.0
            preco_venda = float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0
            lucro = preco_venda - preco_custo
            
            resultado.append({
                'id': estoque.idESTOQUE,
                'produto_id': produto.idPRODUTO,
                'nome': produto.DESCRICAO,
                'preco_custo': preco_custo,
                'preco_venda': preco_venda,
                'quantidade': estoque.QTD_DISPONIVEL,
                'lucro_unitario': lucro,
            })
        
        return resultado
    
    @staticmethod
    @transaction.atomic
    def cadastrar_produto_estoque(dados):
        """Cadastra um novo produto e seu estoque"""
        print(f"[ESTOQUE SERVICE] Cadastrando produto: {dados}")
        
        # Criar produto - IOF guarda preço de custo, VLR_UNIT guarda preço de venda
        # Se for marcado como serviço, não rastreamos estoque (TRACK_STOCK=False)
        is_service = bool(dados.get('is_service', False))
        produto = Produto.objects.create(
            DESCRICAO=dados['nome'],
            VLR_UNIT=str(dados['preco_venda']),
            IOF=str(dados.get('preco_custo', 0)),
            DT_MOVIMENTADA=dados.get('data_movimentacao'),
            TRACK_STOCK=(not is_service)
        )
        
        # Criar estoque
        estoque = Estoque.objects.create(
            PRODUTO_idPRODUTO=produto,
            QTD_DISPONIVEL=dados['quantidade_inicial']
        )
        
        print(f"[ESTOQUE SERVICE] Produto criado ID: {produto.idPRODUTO}, Estoque ID: {estoque.idESTOQUE}")
        
        return {
            'produto': produto,
            'estoque': estoque
        }
    
    @staticmethod
    @transaction.atomic
    def adicionar_reposicao(produto_id, quantidade):
        """Adiciona quantidade ao estoque de um produto"""
        print(f"[ESTOQUE SERVICE] Adicionando {quantidade} unidades ao produto {produto_id}")
        
        try:
            produto = Produto.objects.get(idPRODUTO=produto_id)
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
        
        estoque, created = Estoque.objects.get_or_create(
            PRODUTO_idPRODUTO=produto,
            defaults={'QTD_DISPONIVEL': 0}
        )
        
        estoque.QTD_DISPONIVEL += quantidade
        estoque.save()
        
        print(f"[ESTOQUE SERVICE] Estoque atualizado. Quantidade atual: {estoque.QTD_DISPONIVEL}")
        
        return estoque
    
    @staticmethod
    @transaction.atomic
    def atualizar_produto(produto_id, dados):
        """Atualiza informações completas de um produto"""
        print(f"[ESTOQUE SERVICE] Atualizando produto {produto_id}")
        
        try:
            produto = Produto.objects.get(idPRODUTO=produto_id)
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
        
        # Atualizar produto
        produto.DESCRICAO = dados.get('nome', produto.DESCRICAO)
        produto.VLR_UNIT = str(dados.get('preco_venda', produto.VLR_UNIT))
        produto.IOF = str(dados.get('preco_custo', produto.IOF))
        # Atualizar flag de serviço/controle de estoque se informado
        if 'is_service' in dados:
            produto.TRACK_STOCK = (not bool(dados.get('is_service')))
        produto.save()
        
        print(f"[ESTOQUE SERVICE] Produto atualizado: {produto.DESCRICAO}")
        
        # Atualizar estoque se necessário
        if 'quantidade' in dados:
            estoque = Estoque.objects.filter(PRODUTO_idPRODUTO=produto).first()
            if estoque:
                estoque.QTD_DISPONIVEL = int(dados['quantidade'])
                estoque.save()
                print(f"[ESTOQUE SERVICE] Estoque atualizado: {estoque.QTD_DISPONIVEL}")
        
        return produto
    
    @staticmethod
    def buscar_produto(produto_id):
        """Busca um produto específico com seu estoque"""
        try:
            produto = Produto.objects.only('idPRODUTO', 'DESCRICAO', 'IOF', 'VLR_UNIT', 'TRACK_STOCK').get(idPRODUTO=produto_id)
            estoque = Estoque.objects.filter(PRODUTO_idPRODUTO=produto).only('idESTOQUE', 'QTD_DISPONIVEL').first()
            
            return {
                'produto': produto,
                'estoque': estoque,
                'nome': produto.DESCRICAO,
                'preco_custo': float(produto.IOF) if produto.IOF else 0.0,
                'preco_venda': float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0,
                'quantidade': estoque.QTD_DISPONIVEL if estoque else 0,
                'is_service': not bool(produto.TRACK_STOCK)
            }
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
    
    @staticmethod
    @transaction.atomic
    def deletar_produto(produto_id):
        """Deleta um produto e seu estoque"""
        try:
            produto = Produto.objects.get(idPRODUTO=produto_id)
            nome = produto.DESCRICAO
            
            # Deletar estoque associado
            Estoque.objects.filter(PRODUTO_idPRODUTO=produto).delete()
            
            # Deletar produto
            produto.delete()
            
            print(f"[ESTOQUE SERVICE] Produto '{nome}' (ID: {produto_id}) deletado do banco")
            
            return nome
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")