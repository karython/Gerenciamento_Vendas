# app_controle/services/estoque_services.py
"""
Service de gerenciamento de estoque e produtos
"""

from django.db import transaction
from decimal import Decimal
from ..models import Estoque, Produto


class EstoqueService:
    
    @staticmethod
    def listar_estoque():
        """
        Lista todos os produtos com informações de estoque
        
        Returns:
            list: Lista de dicts com informações dos produtos
        """
        # ✅ Usar novos nomes
        estoques = Estoque.objects.select_related('produto').only(
            'id', 'quantidade_disponivel',  # ✅ Novos nomes
            'produto__id', 'produto__descricao',  # ✅ Novos nomes
            'produto__iof', 'produto__preco_unitario'  # ✅ Novos nomes
        ).order_by('produto__descricao')
        
        resultado = []
        for estoque in estoques.iterator():
            produto = estoque.produto  # ✅ Novo nome
            
            # IOF armazena o preço de custo, preco_unitario o preço de venda
            preco_custo = float(produto.iof) if produto.iof else 0.0  # ✅ Novo nome
            preco_venda = float(produto.preco_unitario)  # ✅ Novo nome
            lucro = preco_venda - preco_custo
            
            resultado.append({
                'id': estoque.id,  # ✅ Novo nome
                'produto_id': produto.id,  # ✅ Novo nome
                'nome': produto.descricao,  # ✅ Novo nome
                'preco_custo': preco_custo,
                'preco_venda': preco_venda,
                'quantidade': estoque.quantidade_disponivel,  # ✅ Novo nome
                'lucro_unitario': lucro,
            })
        
        return resultado
    
    @staticmethod
    @transaction.atomic
    def cadastrar_produto_estoque(dados):
        """
        Cadastra um novo produto e seu estoque
        
        Args:
            dados (dict): Dados do produto
                - nome (str): Nome/descrição do produto
                - preco_venda (float): Preço de venda
                - preco_custo (float, opcional): Preço de custo
                - quantidade_inicial (int): Quantidade inicial em estoque
                - is_service (bool, opcional): Se é um serviço
        
        Returns:
            dict: {'produto': Produto, 'estoque': Estoque}
        """
        # ✅ Criar produto com novos nomes
        is_service = bool(dados.get('is_service', False))
        
        produto = Produto.objects.create(
            descricao=dados['nome'],  # ✅ Novo nome
            preco_unitario=Decimal(str(dados['preco_venda'])),  # ✅ Novo nome
            iof=Decimal(str(dados.get('preco_custo', 0))),  # ✅ Novo nome
            controlar_estoque=(not is_service)  # ✅ Novo nome
        )
        
        # ✅ Criar estoque (novos nomes)
        estoque = Estoque.objects.create(
            produto=produto,  # ✅ Novo nome
            quantidade_disponivel=dados['quantidade_inicial']  # ✅ Novo nome
        )
        
        return {
            'produto': produto,
            'estoque': estoque
        }
    
    @staticmethod
    @transaction.atomic
    def adicionar_reposicao(produto_id, quantidade):
        """
        Adiciona quantidade ao estoque de um produto
        
        Args:
            produto_id (int): ID do produto
            quantidade (int): Quantidade a adicionar
        
        Returns:
            Estoque: Objeto de estoque atualizado
        
        Raises:
            ValueError: Se produto não encontrado
        """
        try:
            # ✅ Buscar produto (novo nome)
            produto = Produto.objects.get(id=produto_id)  # ✅ Novo nome
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
        
        # ✅ Buscar ou criar estoque (novos nomes)
        estoque, _ = Estoque.objects.get_or_create(
            produto=produto,  # ✅ Novo nome
            defaults={'quantidade_disponivel': 0}  # ✅ Novo nome
        )
        
        # ✅ Usar método do model
        estoque.adicionar(quantidade)
        
        return estoque
    
    @staticmethod
    @transaction.atomic
    def atualizar_produto(produto_id, dados):
        """
        Atualiza informações de um produto
        
        Args:
            produto_id (int): ID do produto
            dados (dict): Dados atualizados
        
        Returns:
            Produto: Produto atualizado
        
        Raises:
            ValueError: Se produto não encontrado
        """
        try:
            # ✅ Buscar produto (novo nome)
            produto = Produto.objects.get(id=produto_id)  # ✅ Novo nome
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
        
        # ✅ Atualizar produto (novos nomes)
        produto.descricao = dados.get('nome', produto.descricao)  # ✅ Novo nome
        produto.preco_unitario = Decimal(str(dados.get('preco_venda', produto.preco_unitario)))  # ✅ Novo nome
        produto.iof = Decimal(str(dados.get('preco_custo', produto.iof)))  # ✅ Novo nome
        
        # Atualizar flag de controle de estoque se informado
        if 'is_service' in dados:
            produto.controlar_estoque = (not bool(dados.get('is_service')))  # ✅ Novo nome
        
        produto.save()
        
        # Atualizar estoque se necessário
        if 'quantidade' in dados:
            estoque = Estoque.objects.filter(produto=produto).first()  # ✅ Novo nome
            if estoque:
                estoque.quantidade_disponivel = int(dados['quantidade'])  # ✅ Novo nome
                estoque.save()
        
        return produto
    
    @staticmethod
    def buscar_produto(produto_id):
        """
        Busca um produto específico com seu estoque
        
        Args:
            produto_id (int): ID do produto
        
        Returns:
            dict: Informações do produto e estoque
        
        Raises:
            ValueError: Se produto não encontrado
        """
        try:
            # ✅ Buscar produto (novos nomes)
            produto = Produto.objects.only(
                'id', 'descricao', 'iof', 'preco_unitario', 'controlar_estoque'  # ✅ Novos nomes
            ).get(id=produto_id)  # ✅ Novo nome
            
            # ✅ Buscar estoque (novo nome)
            estoque = Estoque.objects.filter(
                produto=produto  # ✅ Novo nome
            ).only('id', 'quantidade_disponivel').first()  # ✅ Novos nomes
            
            return {
                'produto': produto,
                'estoque': estoque,
                'nome': produto.descricao,  # ✅ Novo nome
                'preco_custo': float(produto.iof) if produto.iof else 0.0,  # ✅ Novo nome
                'preco_venda': float(produto.preco_unitario),  # ✅ Novo nome
                'quantidade': estoque.quantidade_disponivel if estoque else 0,  # ✅ Novo nome
                'is_service': not bool(produto.controlar_estoque)  # ✅ Novo nome
            }
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")
    
    @staticmethod
    @transaction.atomic
    def deletar_produto(produto_id):
        """
        Deleta um produto e seu estoque
        
        Args:
            produto_id (int): ID do produto
        
        Returns:
            str: Nome do produto deletado
        
        Raises:
            ValueError: Se produto não encontrado
        """
        try:
            # ✅ Buscar produto (novo nome)
            produto = Produto.objects.get(id=produto_id)  # ✅ Novo nome
            nome = produto.descricao  # ✅ Novo nome
            
            # Deletar (CASCADE deleta estoque automaticamente)
            produto.delete()
            
            return nome
        except Produto.DoesNotExist:
            raise ValueError("Produto não encontrado")