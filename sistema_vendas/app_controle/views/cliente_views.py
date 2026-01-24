# app_controle/views/cliente_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from ..services.cliente_services import ClienteService
from ..services.auth_services import AuthService
from ..models import Cliente

@AuthService.requer_login
def listar_clientes(request):
    """Lista todos os clientes cadastrados - OTIMIZADO"""
    loja = AuthService.loja_logada(request)
    clientes = ClienteService.listar_clientes()
    
    return render(request, 'clientes.html', {
        'clientes': clientes,
        'loja': loja
    })

@AuthService.requer_login
def criar_cliente(request):
    """Cria um novo cliente via AJAX"""
    if request.method == 'POST':
        try:
            print("=" * 50)
            print("Requisição POST recebida!")
            print(f"Dados POST: {request.POST}")
            
            dados = {
                'nome': request.POST.get('nome'),
                'data_nascimento': request.POST.get('data_nascimento') or None,
                'cpf': request.POST.get('cpf'),
                'telefone': request.POST.get('telefone'),
                'endereco': request.POST.get('endereco'),
                'cidade': request.POST.get('cidade'),
                'estado': request.POST.get('estado'),
                'cep': request.POST.get('cep'),
            }
            
            print(f"Dados processados: {dados}")
            
            cliente = ClienteService.criar_cliente(dados)
            
            print(f"Cliente cadastrado com sucesso! ID: {cliente.idCLIENTE}")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': 'Cliente cadastrado com sucesso!',
                'cliente': {
                    'id': cliente.idCLIENTE,
                    'nome': cliente.NOME_CLIENTE,
                    'cpf': cliente.CPF,
                    'telefone': cliente.TELEFONE
                }
            })
            
        except Exception as e:
            print(f"ERRO ao cadastrar cliente: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return JsonResponse({
                'success': False,
                'message': f'Erro ao cadastrar cliente: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@AuthService.requer_login
def editar_cliente(request, id):
    """Edita um cliente existente"""
    loja = AuthService.loja_logada(request)
    cliente = get_object_or_404(Cliente, idCLIENTE=id)
    
    if request.method == 'POST':
        try:
            print("=" * 50)
            print(f"Editando cliente ID: {id}")
            print(f"Dados POST: {request.POST}")
            
            dados = {
                'nome': request.POST.get('nome'),
                'data_nascimento': request.POST.get('data_nascimento') or None,
                'cpf': request.POST.get('cpf'),
                'telefone': request.POST.get('telefone'),
                'endereco': request.POST.get('endereco'),
                'cidade': request.POST.get('cidade'),
                'estado': request.POST.get('estado'),
                'cep': request.POST.get('cep'),
            }
            
            ClienteService.atualizar_cliente(id, dados)
            
            print(f"Cliente {id} atualizado com sucesso!")
            print("=" * 50)
            
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes')
            
        except Exception as e:
            print(f"ERRO ao atualizar cliente: {str(e)}")
            import traceback
            traceback.print_exc()
            
            messages.error(request, f'Erro ao atualizar cliente: {str(e)}')
    
    return render(request, 'editar_cliente.html', {
        'cliente': cliente,
        'loja': loja
    })

@AuthService.requer_login
def deletar_cliente(request, id):
    """Deleta um cliente (com validação de vendas)"""
    if request.method == 'POST':
        try:
            print(f"[VIEW] Deletando cliente ID: {id}")
            
            # Verificar se tem vendas ANTES de tentar deletar
            quantidade_vendas = ClienteService.verificar_vendas_cliente(id)
            
            if quantidade_vendas > 0:
                # Cliente tem vendas, não pode deletar
                return JsonResponse({
                    'success': False,
                    'message': f'❌ Este cliente possui {quantidade_vendas} venda(s) registrada(s) no sistema. Não é possível excluí-lo.',
                    'has_vendas': True,
                    'quantidade_vendas': quantidade_vendas
                }, status=400)
            
            # Cliente não tem vendas, pode deletar
            nome = ClienteService.deletar_cliente(id)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Cliente {nome} deletado com sucesso!'
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro de validação: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            print(f"[VIEW] ERRO ao deletar cliente: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar cliente: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)