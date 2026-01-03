# app_controle/views/estoque_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from ..services.estoque_services import EstoqueService
from ..models import Produto, Estoque
from datetime import datetime

def estoque(request):
    """Lista todos os produtos em estoque"""
    estoques = EstoqueService.listar_estoque()
    return render(request, 'estoque.html', {'estoques': estoques})

def cadastrar_produto(request):
    """Cadastra um novo produto no estoque"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            print("=" * 50)
            print("[VIEW] Cadastrando novo produto")
            print(f"Dados recebidos: {dados}")
            
            if not dados.get('nome'):
                return JsonResponse({'success': False, 'message': 'Nome do produto é obrigatório'}, status=400)
            
            if not dados.get('preco_venda') or float(dados['preco_venda']) <= 0:
                return JsonResponse({'success': False, 'message': 'Preço de venda inválido'}, status=400)
            
            if not dados.get('quantidade_inicial') or int(dados['quantidade_inicial']) < 0:
                return JsonResponse({'success': False, 'message': 'Quantidade inicial inválida'}, status=400)
            
            dados['data_movimentacao'] = datetime.now()
            
            resultado = EstoqueService.cadastrar_produto_estoque(dados)
            
            print(f"[VIEW] Produto cadastrado com sucesso!")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': 'Produto cadastrado com sucesso!',
                'produto': {
                    'id': resultado['produto'].idPRODUTO,
                    'estoque_id': resultado['estoque'].idESTOQUE,
                    'nome': resultado['produto'].DESCRICAO,
                    'preco': float(resultado['produto'].VLR_UNIT),
                    'quantidade': resultado['estoque'].QTD_DISPONIVEL
                }
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro de validação: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[VIEW] Erro ao cadastrar produto: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def buscar_produto_ajax(request, produto_id):
    """Busca dados de um produto para edição - AJAX"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'message': 'Método inválido'}, status=400)
    
    try:
        print(f"[VIEW] Buscando produto {produto_id}")  # Debug
        
        # Buscar produto
        produto = get_object_or_404(Produto, idPRODUTO=produto_id)
        
        # Buscar estoque
        estoque = Estoque.objects.filter(PRODUTO_idPRODUTO=produto).first()
        
        if not estoque:
            return JsonResponse({
                'success': False, 
                'message': 'Produto sem estoque cadastrado'
            }, status=404)
        
        # Preparar dados para retornar
        dados = {
            'success': True,
            'produto': {
                'id': produto.idPRODUTO,
                'nome': produto.DESCRICAO,
                'preco_custo': float(produto.IOF) if produto.IOF and produto.IOF != '0' else 0.0,
                'preco_venda': float(produto.VLR_UNIT) if produto.VLR_UNIT else 0.0,
                'quantidade': estoque.QTD_DISPONIVEL
            }
        }
        
        print(f"[VIEW] Produto encontrado: {dados}")  # Debug
        
        return JsonResponse(dados)
        
    except Produto.DoesNotExist:
        print(f"[VIEW] Produto {produto_id} não encontrado")
        return JsonResponse({
            'success': False,
            'message': 'Produto não encontrado'
        }, status=404)
    except Exception as e:
        print(f"[VIEW] Erro ao buscar produto: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        }, status=500)

def editar_produto(request, produto_id):
    """Edita um produto"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            print("=" * 50)
            print(f"[VIEW] Editando produto {produto_id}")
            print(f"Dados recebidos: {dados}")
            
            # Validações
            if not dados.get('nome'):
                return JsonResponse({'success': False, 'message': 'Nome é obrigatório'}, status=400)
            
            if not dados.get('preco_venda') or float(dados['preco_venda']) <= 0:
                return JsonResponse({'success': False, 'message': 'Preço de venda inválido'}, status=400)
            
            if 'quantidade' in dados and int(dados['quantidade']) < 0:
                return JsonResponse({'success': False, 'message': 'Quantidade não pode ser negativa'}, status=400)
            
            # Atualizar produto
            produto = EstoqueService.atualizar_produto(produto_id, dados)
            
            print(f"[VIEW] Produto {produto_id} atualizado com sucesso!")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': 'Produto atualizado com sucesso!',
                'produto': {
                    'id': produto.idPRODUTO,
                    'nome': produto.DESCRICAO,
                    'preco_custo': float(produto.IOF) if produto.IOF else 0.0,
                    'preco_venda': float(produto.VLR_UNIT)
                }
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro de validação: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[VIEW] Erro ao editar produto: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def deletar_produto(request, produto_id):
    """Deleta um produto do banco de dados"""
    if request.method == 'POST':
        try:
            print("=" * 50)
            print(f"[VIEW] Deletando produto {produto_id}")
            
            nome = EstoqueService.deletar_produto(produto_id)
            
            print(f"[VIEW] Produto '{nome}' deletado com sucesso!")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': f'Produto "{nome}" deletado com sucesso!'
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[VIEW] Erro ao deletar produto: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

def adicionar_reposicao(request, produto_id):
    """Adiciona reposição ao estoque"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            
            quantidade = int(dados.get('quantidade', 0))
            
            if quantidade <= 0:
                return JsonResponse({'success': False, 'message': 'Quantidade deve ser maior que zero'}, status=400)
            
            print(f"[VIEW] Adicionando {quantidade} unidades ao produto {produto_id}")
            
            estoque = EstoqueService.adicionar_reposicao(produto_id, quantidade)
            
            return JsonResponse({
                'success': True,
                'message': f'{quantidade} unidades adicionadas com sucesso!',
                'nova_quantidade': estoque.QTD_DISPONIVEL
            })
            
        except ValueError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[VIEW] Erro ao adicionar reposição: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)