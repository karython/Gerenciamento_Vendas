# app_controle/views/estoque_views.py
"""
Views de gerenciamento de estoque e produtos
"""

from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from ..services.estoque_services import EstoqueService
from ..services.auth_services import AuthService
from ..models import Produto, Estoque


@AuthService.requer_login
def estoque(request):
    """Lista todos os produtos em estoque - OTIMIZADO"""
    loja = AuthService.loja_logada(request)
    estoques = EstoqueService.listar_estoque()
    
    return render(request, 'estoque/estoque.html', {
        'estoques': estoques,
        'loja': loja
    })


@AuthService.requer_login
def cadastrar_produto(request):
    """Cadastra um novo produto no estoque"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            # Validações
            if not dados.get('nome'):
                return JsonResponse({
                    'success': False,
                    'message': 'Nome do produto é obrigatório'
                }, status=400)
            
            if not dados.get('preco_venda') or float(dados['preco_venda']) <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Preço de venda inválido'
                }, status=400)
            
            if not dados.get('quantidade_inicial') or int(dados['quantidade_inicial']) < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Quantidade inicial inválida'
                }, status=400)
            
            # Cadastrar
            resultado = EstoqueService.cadastrar_produto_estoque(dados)
            
            return JsonResponse({
                'success': True,
                'message': 'Produto cadastrado com sucesso!',
                'produto': {
                    'id': resultado['produto'].id,  # ✅ Novo nome
                    'estoque_id': resultado['estoque'].id,  # ✅ Novo nome
                    'nome': resultado['produto'].descricao,  # ✅ Novo nome
                    'preco': float(resultado['produto'].preco_unitario),  # ✅ Novo nome
                    'quantidade': resultado['estoque'].quantidade_disponivel  # ✅ Novo nome
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)


@AuthService.requer_login
def buscar_produto_ajax(request, produto_id):
    """Busca dados de um produto para edição - AJAX"""
    if request.method != 'GET':
        return JsonResponse({
            'success': False,
            'message': 'Método inválido'
        }, status=400)
    
    try:
        resultado = EstoqueService.buscar_produto(produto_id)

        if not resultado.get('estoque'):
            return JsonResponse({
                'success': False,
                'message': 'Produto sem estoque cadastrado'
            }, status=404)

        return JsonResponse({
            'success': True,
            'produto': {
                'id': resultado['produto'].id,  # ✅ Novo nome
                'nome': resultado['nome'],
                'preco_custo': resultado['preco_custo'],
                'preco_venda': resultado['preco_venda'],
                'quantidade': resultado['quantidade'],
                'is_service': resultado.get('is_service', False)
            }
        })

    except Produto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Produto não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        }, status=500)


@AuthService.requer_login
def editar_produto(request, produto_id):
    """Edita um produto existente"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            # Validações
            if not dados.get('nome'):
                return JsonResponse({
                    'success': False,
                    'message': 'Nome é obrigatório'
                }, status=400)
            
            if not dados.get('preco_venda') or float(dados['preco_venda']) <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Preço de venda inválido'
                }, status=400)
            
            if 'quantidade' in dados and int(dados['quantidade']) < 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Quantidade não pode ser negativa'
                }, status=400)
            
            # Atualizar
            produto = EstoqueService.atualizar_produto(produto_id, dados)
            
            return JsonResponse({
                'success': True,
                'message': 'Produto atualizado com sucesso!',
                'produto': {
                    'id': produto.id,  # ✅ Novo nome
                    'nome': produto.descricao,  # ✅ Novo nome
                    'preco_custo': float(produto.iof) if produto.iof else 0.0,  # ✅ Novo nome
                    'preco_venda': float(produto.preco_unitario)  # ✅ Novo nome
                }
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)


@AuthService.requer_login
def deletar_produto(request, produto_id):
    """Deleta um produto do banco de dados"""
    if request.method == 'POST':
        try:
            nome = EstoqueService.deletar_produto(produto_id)
            
            return JsonResponse({
                'success': True,
                'message': f'Produto "{nome}" deletado com sucesso!'
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)


@AuthService.requer_login
def adicionar_reposicao(request, produto_id):
    """Adiciona reposição ao estoque"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            quantidade = int(dados.get('quantidade', 0))
            
            if quantidade <= 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Quantidade deve ser maior que zero'
                }, status=400)
            
            estoque = EstoqueService.adicionar_reposicao(produto_id, quantidade)
            
            return JsonResponse({
                'success': True,
                'message': f'{quantidade} unidades adicionadas com sucesso!',
                'nova_quantidade': estoque.quantidade_disponivel  # ✅ Novo nome
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)