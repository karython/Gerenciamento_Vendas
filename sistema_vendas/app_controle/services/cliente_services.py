# app_controle/services/cliente_services.py
from django.db import transaction
from django.db.models import Prefetch
from ..models import Cliente, Endereco, Cidades, UF  # ← Corrigir importação

class ClienteService:
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados):
        """
        Cria um cliente com endereço
        """
        print(f"Criando cliente com dados: {dados}")  # Debug
        
        # Criar o cliente
        cliente = Cliente.objects.create(
            NOME_CLIENTE=dados.get('nome'),
            DATA_NASCIMENTO=dados.get('data_nascimento') if dados.get('data_nascimento') else None,
            CPF=dados.get('cpf'),
            TELEFONE=dados.get('telefone')
        )
        
        print(f"Cliente criado com ID: {cliente.idCLIENTE}")
        
        # Se houver informações de endereço, criar o endereço
        if dados.get('endereco') or dados.get('cidade'):
            estado_nome = dados.get('estado', 'DF')
            uf, _ = UF.objects.get_or_create(NOME_ESTADO=estado_nome)
            
            cidade_nome = dados.get('cidade', 'Cidade não informada')
            cidade, _ = Cidades.objects.get_or_create(
                NOME_CIDADE=cidade_nome,
                UF_idUF=uf
            )
            
            Endereco.objects.create(
                LOGRADOURO=dados.get('endereco', ''),
                CEP=dados.get('cep', ''),
                CIDADES_idCIDADES=cidade,
                CLIENTE_idCLIENTE=cliente,
                NUMERO='',
                REFERENCIA=''
            )
            
            print(f"Endereço criado para o cliente {cliente.idCLIENTE}")
        
        return cliente
    
    @staticmethod
    def listar_clientes():
        """
        Lista todos os clientes com seus endereços
        """
        clientes = Cliente.objects.prefetch_related('enderecos').all().order_by('-idCLIENTE')
        print(f"[SERVICE] Total de clientes encontrados: {clientes.count()}")  # Debug
        for c in clientes:
            print(f"[SERVICE] Cliente: ID={c.idCLIENTE}, Nome={c.NOME_CLIENTE}, CPF={c.CPF}")  # Debug
        return clientes
    
    @staticmethod
    def buscar_cliente(cliente_id):
        """
        Busca um cliente específico
        """
        return Cliente.objects.prefetch_related('enderecos').get(idCLIENTE=cliente_id)
    
    @staticmethod
    @transaction.atomic
    def atualizar_cliente(cliente_id, dados):
        """
        Atualiza informações do cliente e endereço
        """
        print(f"Atualizando cliente {cliente_id} com dados: {dados}")  # Debug
        
        # Atualizar cliente
        cliente = Cliente.objects.get(idCLIENTE=cliente_id)
        
        cliente.NOME_CLIENTE = dados.get('nome', cliente.NOME_CLIENTE)
        cliente.DATA_NASCIMENTO = dados.get('data_nascimento') if dados.get('data_nascimento') else None
        cliente.CPF = dados.get('cpf', cliente.CPF)
        cliente.TELEFONE = dados.get('telefone', cliente.TELEFONE)
        cliente.save()
        
        print(f"Cliente {cliente_id} atualizado")
        
        # Atualizar ou criar endereço
        if dados.get('endereco') or dados.get('cidade'):
            # Buscar ou criar UF
            estado_nome = dados.get('estado', 'DF')
            uf, _ = UF.objects.get_or_create(NOME_ESTADO=estado_nome)
            
            # Buscar ou criar Cidade
            cidade_nome = dados.get('cidade', 'Cidade não informada')
            cidade, _ = Cidades.objects.get_or_create(
                NOME_CIDADE=cidade_nome,
                UF_idUF=uf
            )
            
            # Verificar se já existe endereço
            endereco_existente = cliente.enderecos.first()
            
            if endereco_existente:
                # Atualizar endereço existente
                endereco_existente.LOGRADOURO = dados.get('endereco', '')
                endereco_existente.CEP = dados.get('cep', '')
                endereco_existente.CIDADES_idCIDADES = cidade
                endereco_existente.save()
                print(f"Endereço {endereco_existente.idENDERECO} atualizado")
            else:
                # Criar novo endereço
                Endereco.objects.create(
                    LOGRADOURO=dados.get('endereco', ''),
                    CEP=dados.get('cep', ''),
                    CIDADES_idCIDADES=cidade,
                    CLIENTE_idCLIENTE=cliente,
                    NUMERO='',
                    REFERENCIA=''
                )
                print(f"Novo endereço criado para cliente {cliente_id}")
        
        return cliente
    
    @staticmethod
    def deletar_cliente(cliente_id):
        """
        Deleta um cliente
        """
        cliente = Cliente.objects.get(idCLIENTE=cliente_id)
        nome = cliente.NOME_CLIENTE
        cliente.delete()
        print(f"Cliente {nome} (ID: {cliente_id}) deletado")
        return nome