# app_controle/services/cliente_services.py
"""
Service de gerenciamento de clientes
"""

from django.db import transaction
from ..models import Cliente, Venda, Endereco, Cidade, UF


class ClienteService:
    
    @staticmethod
    def listar_clientes():
        """
        Retorna queryset de todos os clientes
        
        Returns:
            QuerySet: Clientes ordenados por nome
        """
        # ✅ Usar novo nome
        return Cliente.objects.order_by('nome')  # ✅ Novo nome
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados):
        """
        Cria um novo cliente e seu endereço
        
        Args:
            dados (dict): Dados do cliente
                - nome (str): Nome completo
                - cpf (str): CPF
                - telefone (str): Telefone
                - data_nascimento (date, opcional): Data de nascimento
                - email (str, opcional): Email
                - logradouro (str, opcional): Endereço
                - numero (str, opcional): Número
                - bairro (str, opcional): Bairro
                - cep (str, opcional): CEP
                - cidade (str, opcional): Nome da cidade
                - estado (str, opcional): Sigla do estado
        
        Returns:
            Cliente: Cliente criado
        """
        # ✅ Criar cliente com novos nomes
        cliente = Cliente.objects.create(
            nome=dados['nome'],  # ✅ Novo nome
            data_nascimento=dados.get('data_nascimento'),  # ✅ Novo nome
            cpf=dados['cpf'],  # ✅ Novo nome
            telefone=dados['telefone'],  # ✅ Novo nome
            email=dados.get('email', ''),  # ✅ Novo nome
        )
        
        # Criar endereço se informado
        logradouro = dados.get('logradouro') or dados.get('endereco')  # Compatibilidade
        cidade_nome = dados.get('cidade')
        estado_sigla = dados.get('estado')
        cep = dados.get('cep')
        
        if logradouro and cidade_nome and estado_sigla:
            try:
                # ✅ Buscar ou criar UF (novo nome)
                uf, _ = UF.objects.get_or_create(
                    sigla=estado_sigla.upper(),  # ✅ Novo nome
                    defaults={'nome': estado_sigla.upper()}  # ✅ Novo nome
                )
                
                # ✅ Buscar ou criar Cidade (novo nome)
                cidade, _ = Cidade.objects.get_or_create(
                    nome=cidade_nome,  # ✅ Novo nome
                    uf=uf,  # ✅ Novo nome
                    defaults={'uf': uf}
                )
                
                # ✅ Criar endereço (novos nomes)
                Endereco.objects.create(
                    cliente=cliente,  # ✅ Novo nome
                    logradouro=logradouro,  # ✅ Novo nome
                    numero=dados.get('numero', ''),  # ✅ Novo nome
                    bairro=dados.get('bairro', ''),  # ✅ Novo nome
                    cep=cep or '',  # ✅ Novo nome
                    cidade=cidade,  # ✅ Novo nome
                    principal=True  # ✅ Marcar como principal
                )
            except Exception as e:
                # Não falhar se endereço der erro
                pass
        
        return cliente
    
    @staticmethod
    @transaction.atomic
    def atualizar_cliente(cliente_id, dados):
        """
        Atualiza um cliente existente e seu endereço
        
        Args:
            cliente_id (int): ID do cliente
            dados (dict): Dados atualizados
        
        Returns:
            Cliente: Cliente atualizado
        """
        # ✅ Buscar cliente (novo nome)
        cliente = Cliente.objects.get(id=cliente_id)  # ✅ Novo nome
        
        # ✅ Atualizar campos (novos nomes)
        cliente.nome = dados['nome']  # ✅ Novo nome
        cliente.data_nascimento = dados.get('data_nascimento')  # ✅ Novo nome
        cliente.cpf = dados['cpf']  # ✅ Novo nome
        cliente.telefone = dados['telefone']  # ✅ Novo nome
        cliente.email = dados.get('email', '')  # ✅ Novo nome
        cliente.save()
        
        # Atualizar endereço
        logradouro = dados.get('logradouro') or dados.get('endereco')
        cidade_nome = dados.get('cidade')
        estado_sigla = dados.get('estado')
        cep = dados.get('cep')
        
        if logradouro and cidade_nome and estado_sigla:
            try:
                # ✅ Buscar ou criar UF
                uf, _ = UF.objects.get_or_create(
                    sigla=estado_sigla.upper(),  # ✅ Novo nome
                    defaults={'nome': estado_sigla.upper()}
                )
                
                # ✅ Buscar ou criar Cidade
                cidade, _ = Cidade.objects.get_or_create(
                    nome=cidade_nome,  # ✅ Novo nome
                    uf=uf,  # ✅ Novo nome
                )
                
                # ✅ Buscar ou criar endereço (novos nomes)
                endereco_obj, criado = Endereco.objects.get_or_create(
                    cliente=cliente,  # ✅ Novo nome
                    principal=True,
                    defaults={
                        'logradouro': logradouro,  # ✅ Novo nome
                        'numero': dados.get('numero', ''),  # ✅ Novo nome
                        'bairro': dados.get('bairro', ''),  # ✅ Novo nome
                        'cep': cep or '',  # ✅ Novo nome
                        'cidade': cidade  # ✅ Novo nome
                    }
                )
                
                # Se já existia, atualizar
                if not criado:
                    endereco_obj.logradouro = logradouro
                    endereco_obj.numero = dados.get('numero', '')
                    endereco_obj.bairro = dados.get('bairro', '')
                    endereco_obj.cep = cep or ''
                    endereco_obj.cidade = cidade
                    endereco_obj.save()
            except Exception as e:
                pass
        
        return cliente
    
    @staticmethod
    def verificar_vendas_cliente(cliente_id):
        """
        Verifica se o cliente possui vendas registradas
        
        Args:
            cliente_id (int): ID do cliente
        
        Returns:
            int: Quantidade de vendas do cliente
        """
        # ✅ Usar novo nome (lookup por id)
        return Venda.objects.filter(cliente_id=cliente_id).count()
    
    @staticmethod
    @transaction.atomic
    def deletar_cliente(cliente_id):
        """
        Deleta um cliente do banco de dados
        
        Args:
            cliente_id (int): ID do cliente
        
        Returns:
            str: Nome do cliente deletado
        
        Raises:
            ValueError: Se o cliente possui vendas registradas
        """
        try:
            # ✅ Buscar cliente (novo nome)
            cliente = Cliente.objects.get(id=cliente_id)  # ✅ Novo nome
            nome_cliente = cliente.nome  # ✅ Novo nome
            
            # Verificar se tem vendas
            quantidade_vendas = ClienteService.verificar_vendas_cliente(cliente_id)
            
            if quantidade_vendas > 0:
                raise ValueError(
                    f"Não é possível excluir o cliente '{nome_cliente}' pois ele possui "
                    f"{quantidade_vendas} venda(s) registrada(s) no sistema."
                )
            
            # Deletar (CASCADE deleta endereços automaticamente)
            cliente.delete()
            
            return nome_cliente
            
        except Cliente.DoesNotExist:
            raise ValueError("Cliente não encontrado")