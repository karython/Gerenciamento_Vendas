# app_controle/views/vendas_views.py

from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService

@AuthService.requer_login
def vendas(request):
    """Lista todas as vendas com filtros por data e nome - OTIMIZADO"""
    loja = AuthService.loja_logada(request)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca_nome = request.GET.get('busca_nome')
    
    vendas_lista = VendaService.listar_vendas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca_nome=busca_nome
    )
    
    context = {
        'vendas': vendas_lista,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'busca_nome': busca_nome,
        'loja': loja
    }
    
    return render(request, 'vendas.html', context)

@AuthService.requer_login
def deletar_venda(request, venda_id):
    """Deleta uma venda do sistema"""
    if request.method == 'POST':
        try:
            print(f"[VIEW] Deletando venda ID: {venda_id}")
            
            venda_numero = VendaService.deletar_venda(venda_id)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Venda {venda_numero} deletada com sucesso!'
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro de validação: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            print(f"[VIEW] ERRO ao deletar venda: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar venda: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)

@AuthService.requer_login
def deletar_vendas_multiplas(request):
    """Deleta múltiplas vendas de uma vez"""
    if request.method == 'POST':
        try:
            import json
            dados = json.loads(request.body)
            vendas_ids = dados.get('vendas_ids', [])
            
            if not vendas_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'Nenhuma venda selecionada'
                }, status=400)
            
            print(f"[VIEW] Deletando {len(vendas_ids)} vendas: {vendas_ids}")
            
            vendas_deletadas = []
            erros = []
            
            for venda_id in vendas_ids:
                try:
                    venda_numero = VendaService.deletar_venda(venda_id)
                    vendas_deletadas.append(venda_numero)
                except Exception as e:
                    erros.append(f"Venda {venda_id}: {str(e)}")
            
            if erros:
                return JsonResponse({
                    'success': False,
                    'message': f'Algumas vendas não foram deletadas: {", ".join(erros)}',
                    'deletadas': len(vendas_deletadas),
                    'erros': len(erros)
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ {len(vendas_deletadas)} venda(s) deletada(s) com sucesso!',
                'deletadas': len(vendas_deletadas)
            })
            
        except Exception as e:
            print(f"[VIEW] ERRO ao deletar vendas múltiplas: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar vendas: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)