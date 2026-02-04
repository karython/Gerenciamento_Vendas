# app_controle/views/vendas_views.py

from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from ..models import Orcamento, Venda, ItemVenda

@AuthService.requer_login
def vendas(request):
    """Lista todas as vendas e orçamentos com filtros por tipo, data e nome"""
    loja = AuthService.loja_logada(request)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca_nome = request.GET.get('busca_nome')
    tipo_filtro = request.GET.get('tipo', 'todas')  # 'vendas', 'orcamentos' ou 'todas'
    
    vendas_lista = VendaService.listar_vendas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca_nome=busca_nome
    )
    
    orcamentos_lista = []
    if tipo_filtro in ['orcamentos', 'todas']:
        orcamentos = Orcamento.objects.select_related('CLIENTE_idCLIENTE', 'PAGAMENTO_idPAGAMENTO').all()
        
        # Filtro por nome do cliente
        if busca_nome:
            orcamentos = orcamentos.filter(CLIENTE_idCLIENTE__NOME_CLIENTE__icontains=busca_nome)
        
        # Filtro por data
        if data_inicio:
            from django.utils.dateparse import parse_date
            dt_inicio = parse_date(data_inicio)
            if dt_inicio:
                orcamentos = orcamentos.filter(DT_ORCAMENTO__date__gte=dt_inicio)
        
        if data_fim:
            from django.utils.dateparse import parse_date
            dt_fim = parse_date(data_fim)
            if dt_fim:
                orcamentos = orcamentos.filter(DT_ORCAMENTO__date__lte=dt_fim)
        
        orcamentos_lista = list(orcamentos)
    
    # Filtrar por tipo
    if tipo_filtro == 'vendas':
        orcamentos_lista = []
    elif tipo_filtro == 'orcamentos':
        vendas_lista = []
    
    context = {
        'vendas': vendas_lista,
        'orcamentos': orcamentos_lista,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'busca_nome': busca_nome,
        'tipo_filtro': tipo_filtro,
        'loja': loja
    }
    
    return render(request, 'vendas.html', context)

@AuthService.requer_login
def orcamentos(request):
    """Lista apenas orçamentos com filtros"""
    loja = AuthService.loja_logada(request)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca_nome = request.GET.get('busca_nome')
    status_filtro = request.GET.get('status', 'todos')  # 'PENDENTE', 'APROVADO', etc ou 'todos'
    
    orcamentos_lista = Orcamento.objects.select_related('CLIENTE_idCLIENTE', 'PAGAMENTO_idPAGAMENTO').all()
    
    # Filtro por nome do cliente
    if busca_nome:
        orcamentos_lista = orcamentos_lista.filter(CLIENTE_idCLIENTE__NOME_CLIENTE__icontains=busca_nome)
    
    # Filtro por data
    if data_inicio:
        from django.utils.dateparse import parse_date
        dt_inicio = parse_date(data_inicio)
        if dt_inicio:
            orcamentos_lista = orcamentos_lista.filter(DT_ORCAMENTO__date__gte=dt_inicio)
    
    if data_fim:
        from django.utils.dateparse import parse_date
        dt_fim = parse_date(data_fim)
        if dt_fim:
            orcamentos_lista = orcamentos_lista.filter(DT_ORCAMENTO__date__lte=dt_fim)
    
    # Filtrar por status se necessário
    if status_filtro != 'todos':
        orcamentos_lista = orcamentos_lista.filter(STATUS=status_filtro)
    
    # Ordenar por data decrescente
    orcamentos_lista = orcamentos_lista.order_by('-DT_ORCAMENTO')
    
    context = {
        'orcamentos': orcamentos_lista,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'busca_nome': busca_nome,
        'status_filtro': status_filtro,
        'loja': loja
    }
    
    return render(request, 'orcamentos.html', context)

@AuthService.requer_login
def detalhes_venda(request, venda_id):
    """
    Retorna os detalhes completos de uma venda incluindo os produtos
    """
    try:
        venda = Venda.objects.select_related(
            'CLIENTE_idCLIENTE', 
            'PAGAMENTO_idPAGAMENTO'
        ).get(idVENDA=venda_id)
        
        # Buscar os itens da venda
        itens = ItemVenda.objects.filter(
            VENDA_idVENDA=venda
        ).select_related('PRODUTO_idPRODUTO')
        
        # Montar lista de produtos
        produtos = []
        for item in itens:
            produtos.append({
                'nome': item.PRODUTO_idPRODUTO.NOME_PRODUTO,
                'quantidade': item.QTD_ITEM,
                'total': f"{item.VLR_ITEM:.2f}".replace('.', ',')
            })
        
        # Montar dados da venda
        dados_venda = {
            'numero': f"V-{venda.idVENDA:05d}",
            'cliente': venda.CLIENTE_idCLIENTE.NOME_CLIENTE,
            'telefone': venda.CLIENTE_idCLIENTE.TELEFONE or 'Não informado',
            'data': venda.DT_VENDA.strftime('%d/%m/%Y %H:%M'),
            'total': f"{venda.VLR_TOTAL:.2f}".replace('.', ','),
            'formaPagamento': venda.PAGAMENTO_idPAGAMENTO.TP_PAGAMENTO,
            'produtos': produtos,
            'observacao': venda.OBSERVACAO if getattr(venda, 'OBSERVACAO', None) else '',
            'urlPdf': f"/vendas/pdf/{venda.idVENDA}/"  # Ajuste conforme sua URL
        }
        
        return JsonResponse({
            'success': True,
            'venda': dados_venda
        })
        
    except Venda.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Venda não encontrada'
        }, status=404)
        
    except Exception as e:
        print(f"[VIEW] Erro ao buscar detalhes da venda: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar detalhes: {str(e)}'
        }, status=500)

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

@AuthService.requer_login
def deletar_orcamento(request, orcamento_id):
    """Deleta um orçamento do sistema"""
    if request.method == 'POST':
        try:
            print(f"[VIEW] Deletando orçamento ID: {orcamento_id}")
            
            orcamento = Orcamento.objects.get(idORCAMENTO=orcamento_id)
            orcamento_numero = orcamento.idORCAMENTO
            orcamento.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Orçamento {orcamento_numero} deletado com sucesso!'
            })
            
        except Orcamento.DoesNotExist:
            print(f"[VIEW] Orçamento não encontrado: {orcamento_id}")
            return JsonResponse({
                'success': False,
                'message': 'Orçamento não encontrado'
            }, status=404)
        except Exception as e:
            print(f"[VIEW] Erro ao deletar orçamento: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar orçamento: {str(e)}'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)