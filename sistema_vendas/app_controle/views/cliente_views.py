# app_controle/views/cliente_views.py
"""
Views de gerenciamento de clientes
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse
from ..services.cliente_services import ClienteService
from ..services.auth_services import AuthService
from ..models import Cliente
from ..forms import ClienteForm  # ✅ IMPORTAR


@AuthService.requer_login
def listar_clientes(request):
    """Lista todos os clientes cadastrados - OTIMIZADO"""
    loja = AuthService.loja_logada(request)
    page = request.GET.get('page', 1)
    per_page = 25

    clientes_qs = (
        Cliente.objects
        .only('id', 'nome', 'cpf', 'telefone')
        .order_by('nome')
    )
    
    paginator = Paginator(clientes_qs, per_page)
    clientes_page = paginator.get_page(page)

    return render(request, 'clientes/clientes.html', {
        'clientes': clientes_page,
        'loja': loja,
        'paginator': paginator,
        'page_obj': clientes_page,
    })


@AuthService.requer_login
def criar_cliente(request):
    """Cria um novo cliente via AJAX"""
    if request.method == 'POST':
        # ✅ Usar Form
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            try:
                # ✅ Form já formatou e validou tudo
                cliente = ClienteService.criar_cliente(form.cleaned_data)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Cliente cadastrado com sucesso!',
                    'cliente': {
                        'id': cliente.id,
                        'nome': cliente.nome,
                        'cpf': cliente.cpf,
                        'telefone': cliente.telefone
                    }
                })
                
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Erro ao cadastrar cliente: {str(e)}'
                }, status=400)
        else:
            # ✅ Retornar erros do form
            errors = []
            for field, errs in form.errors.items():
                for err in errs:
                    errors.append(f"{form.fields[field].label}: {err}")
            
            return JsonResponse({
                'success': False,
                'message': '; '.join(errors)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)


@AuthService.requer_login
def editar_cliente(request, id):
    """Edita um cliente existente"""
    loja = AuthService.loja_logada(request)
    cliente = get_object_or_404(Cliente, id=id)
    
    if request.method == 'POST':
        # ✅ Usar Form com instance (para edição)
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            try:
                # ✅ Salvar com dados validados
                ClienteService.atualizar_cliente(id, form.cleaned_data)
                
                messages.success(request, 'Cliente atualizado com sucesso!')
                return redirect('clientes')
                
            except Exception as e:
                messages.error(request, f'Erro ao atualizar cliente: {str(e)}')
        else:
            # ✅ Mostrar erros
            for error in form.errors.values():
                for err in error:
                    messages.error(request, err)
    else:
        initial_data = {
            'nome': cliente.nome,
            'cpf': cliente.cpf,
            'telefone': cliente.telefone,
            'email': cliente.email,
            'data_nascimento': cliente.data_nascimento,
        }

        endereco = cliente.enderecos.select_related('cidade__uf').filter(principal=True).first()
        if endereco:
            initial_data.update({
                'logradouro': endereco.logradouro,
                'numero': endereco.numero,
                'bairro': endereco.bairro,
                'cep': endereco.cep,
                'cidade': endereco.cidade.nome,
                'estado': endereco.cidade.uf.sigla,
            })

        form = ClienteForm(initial=initial_data, instance=cliente)

    endereco = cliente.enderecos.select_related('cidade__uf').filter(principal=True).first()

    return render(request, 'clientes/editar_cliente.html', {
        'form': form,
        'cliente': cliente,
        'endereco': endereco,
        'loja': loja
    })


@AuthService.requer_login
def deletar_cliente(request, id):
    """Deleta um cliente (com validação de vendas)"""
    if request.method == 'POST':
        try:
            # Verificar vendas
            quantidade_vendas = ClienteService.verificar_vendas_cliente(id)
            
            if quantidade_vendas > 0:
                return JsonResponse({
                    'success': False,
                    'message': (
                        f'❌ Este cliente possui {quantidade_vendas} venda(s) '
                        'registrada(s). Não é possível excluí-lo.'
                    ),
                    'has_vendas': True,
                    'quantidade_vendas': quantidade_vendas
                }, status=400)
            
            # Deletar
            nome = ClienteService.deletar_cliente(id)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Cliente {nome} deletado com sucesso!'
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar cliente: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)