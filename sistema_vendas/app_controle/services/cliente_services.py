# app_controle/services/cliente_services.py

from django.db import transaction
from ..models import Cliente, Venda

class ClienteService:
    
    @staticmethod
    def listar_clientes():
        """Retorna todos os clientes cadastrados"""
        return Cliente.objects.all().order_by('NOME_CLIENTE')
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados):
        """Cria um novo cliente"""
        print("=" * 50)
        print(f"[CLIENTE SERVICE] Criando cliente: {dados.get('nome')}")
        
        cliente = Cliente.objects.create(
            NOME_CLIENTE=dados['nome'],
            DATA_NASCIMENTO=dados.get('data_nascimento'),
            CPF=dados['cpf'],
            TELEFONE=dados['telefone'],
            EMAIL=dados.get('email', ''),
        )
        
        print(f"[CLIENTE SERVICE] ✅ Cliente '{cliente.NOME_CLIENTE}' criado com ID: {cliente.idCLIENTE}")
        print("=" * 50)
        
        return cliente
    
    @staticmethod
    @transaction.atomic
    def atualizar_cliente(cliente_id, dados):
        """Atualiza um cliente existente"""
        print("=" * 50)
        print(f"[CLIENTE SERVICE] Atualizando cliente ID: {cliente_id}")
        
        cliente = Cliente.objects.get(idCLIENTE=cliente_id)
        
        cliente.NOME_CLIENTE = dados['nome']
        cliente.DATA_NASCIMENTO = dados.get('data_nascimento')
        cliente.CPF = dados['cpf']
        cliente.TELEFONE = dados['telefone']
        cliente.EMAIL = dados.get('email', '')
        
        cliente.save()
        
        print(f"[CLIENTE SERVICE] ✅ Cliente '{cliente.NOME_CLIENTE}' atualizado!")
        print("=" * 50)
        
        return cliente
    
    @staticmethod
    def verificar_vendas_cliente(cliente_id):
        """Verifica se o cliente possui vendas registradas"""
        vendas = Venda.objects.filter(CLIENTE_idCLIENTE_id=cliente_id)
        return vendas.count()
    
    @staticmethod
    @transaction.atomic
    def deletar_cliente(cliente_id):
        """
        Deleta um cliente do banco de dados
        
        Raises:
            ValueError: Se o cliente possui vendas registradas
        """
        print("=" * 50)
        print(f"[CLIENTE SERVICE] Tentando deletar cliente ID: {cliente_id}")
        
        try:
            cliente = Cliente.objects.get(idCLIENTE=cliente_id)
            nome_cliente = cliente.NOME_CLIENTE
            
            # Verificar se tem vendas
            quantidade_vendas = ClienteService.verificar_vendas_cliente(cliente_id)
            
            if quantidade_vendas > 0:
                print(f"[CLIENTE SERVICE] ❌ Cliente possui {quantidade_vendas} venda(s) registrada(s)")
                raise ValueError(
                    f"Não é possível excluir o cliente '{nome_cliente}' pois ele possui "
                    f"{quantidade_vendas} venda(s) registrada(s) no sistema. "
                    f"Para excluir este cliente, primeiro remova as vendas associadas a ele."
                )
            
            # Se não tem vendas, pode deletar
            cliente.delete()
            
            print(f"[CLIENTE SERVICE] ✅ Cliente '{nome_cliente}' deletado com sucesso!")
            print("=" * 50)
            
            return nome_cliente
            
        except Cliente.DoesNotExist:
            print(f"[CLIENTE SERVICE] ❌ Cliente {cliente_id} não encontrado")
            raise ValueError(f"Cliente não encontrado")