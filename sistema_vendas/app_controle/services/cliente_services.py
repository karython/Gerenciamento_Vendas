# app_controle/services/cliente_services.py

from django.db import transaction
from ..models import Cliente, Venda, Endereco, Cidades, UF

class ClienteService:
    
    @staticmethod
    def listar_clientes():
        """Retorna todos os clientes cadastrados"""
        return Cliente.objects.all().order_by('NOME_CLIENTE')
    
    @staticmethod
    @transaction.atomic
    def criar_cliente(dados):
        """Cria um novo cliente e seu endereço"""
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
        
        # Criar endereço se informado
        endereco = dados.get('endereco')
        cidade_nome = dados.get('cidade')
        estado = dados.get('estado')
        cep = dados.get('cep')
        
        if endereco and cidade_nome and estado:
            try:
                # Buscar ou criar UF
                uf, criado_uf = UF.objects.get_or_create(
                    NOME_ESTADO=estado,
                    defaults={}
                )
                if criado_uf:
                    print(f"[CLIENTE SERVICE] ℹ️ UF '{estado}' criada")
                
                # Buscar ou criar Cidade
                cidade, criado_cidade = Cidades.objects.get_or_create(
                    NOME_CIDADE=cidade_nome,
                    UF_idUF=uf,
                    defaults={'UF_idUF': uf}
                )
                if criado_cidade:
                    print(f"[CLIENTE SERVICE] ℹ️ Cidade '{cidade_nome}' criada")
                
                # Criar endereço
                Endereco.objects.create(
                    LOGRADOURO=endereco,
                    NUMERO=dados.get('numero', ''),
                    BAIRRO=dados.get('bairro', ''),
                    CEP=cep or '',
                    CIDADES_idCIDADES=cidade,
                    CLIENTE_idCLIENTE=cliente
                )
                print(f"[CLIENTE SERVICE] ✅ Endereço criado para o cliente")
            except Exception as e:
                print(f"[CLIENTE SERVICE] ⚠️ Erro ao criar endereço: {str(e)}")
        
        print("=" * 50)
        return cliente
    
    @staticmethod
    @transaction.atomic
    def atualizar_cliente(cliente_id, dados):
        """Atualiza um cliente existente e seu endereço"""
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
        
        # Atualizar endereço
        endereco = dados.get('endereco')
        cidade_nome = dados.get('cidade')
        estado = dados.get('estado')
        cep = dados.get('cep')
        
        if endereco and cidade_nome and estado:
            try:
                # Buscar ou criar UF
                uf, criado_uf = UF.objects.get_or_create(
                    NOME_ESTADO=estado,
                    defaults={}
                )
                if criado_uf:
                    print(f"[CLIENTE SERVICE] ℹ️ UF '{estado}' criada")
                
                # Buscar ou criar Cidade
                cidade, criado_cidade = Cidades.objects.get_or_create(
                    NOME_CIDADE=cidade_nome,
                    UF_idUF=uf,
                    defaults={'UF_idUF': uf}
                )
                if criado_cidade:
                    print(f"[CLIENTE SERVICE] ℹ️ Cidade '{cidade_nome}' criada")
                
                # Buscar ou criar endereço
                endereco_obj, criado = Endereco.objects.get_or_create(
                    CLIENTE_idCLIENTE=cliente,
                    defaults={
                        'LOGRADOURO': endereco,
                        'NUMERO': dados.get('numero', ''),
                        'BAIRRO': dados.get('bairro', ''),
                        'CEP': cep or '',
                        'CIDADES_idCIDADES': cidade
                    }
                )
                
                # Se já existia, atualizar
                if not criado:
                    endereco_obj.LOGRADOURO = endereco
                    endereco_obj.NUMERO = dados.get('numero', '')
                    endereco_obj.BAIRRO = dados.get('bairro', '')
                    endereco_obj.CEP = cep or ''
                    endereco_obj.CIDADES_idCIDADES = cidade
                    endereco_obj.save()
                    print(f"[CLIENTE SERVICE] ✅ Endereço atualizado")
                else:
                    print(f"[CLIENTE SERVICE] ✅ Endereço criado")
            except Exception as e:
                print(f"[CLIENTE SERVICE] ⚠️ Erro ao atualizar endereço: {str(e)}")
        
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