# app_controle/views/vendas_views.py
"""
Views de listagem e gerenciamento de vendas
"""

from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import JsonResponse
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from ..models import Orcamento, Venda, ItemVenda


@AuthService.requer_login
def vendas(request):
    """Lista todas as vendas e orçamentos com filtros"""
    loja = AuthService.loja_logada(request)
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca_nome = request.GET.get('busca_nome')
    tipo_filtro = request.GET.get('tipo', 'todas')
    
    # Listar vendas
    vendas_lista = VendaService.listar_vendas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca_nome=busca_nome
    )
    
    # Listar orçamentos se necessário
    orcamentos_lista = []
    if tipo_filtro in ['orcamentos', 'todas']:
        # ✅ Usar novos nomes
        orcamentos = Orcamento.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        ).only(
            'id', 'data_orcamento', 'total', 'status',  # ✅ Novos nomes
            'cliente__nome', 'cliente__telefone',  # ✅ Novos nomes
            'forma_pagamento__nome'  # ✅ Novo nome
        )

        # Filtro por nome
        if busca_nome:
            orcamentos = orcamentos.filter(cliente__nome__icontains=busca_nome)  # ✅ Novo nome

        # Filtro por data
        if data_inicio:
            from django.utils.dateparse import parse_date
            dt_inicio = parse_date(data_inicio)
            if dt_inicio:
                orcamentos = orcamentos.filter(data_orcamento__date__gte=dt_inicio)  # ✅ Novo nome

        if data_fim:
            from django.utils.dateparse import parse_date
            dt_fim = parse_date(data_fim)
            if dt_fim:
                orcamentos = orcamentos.filter(data_orcamento__date__lte=dt_fim)  # ✅ Novo nome

        orcamentos_lista = orcamentos
    
    # Filtrar por tipo
    if tipo_filtro == 'vendas':
        orcamentos_lista = []
    elif tipo_filtro == 'orcamentos':
        vendas_lista = []

    # Paginação
    page = request.GET.get('page', 1)
    per_page = 25

    paginator_vendas = Paginator(vendas_lista, per_page)
    vendas_page = paginator_vendas.get_page(page)

    paginator_orc = Paginator(orcamentos_lista, per_page)
    orcamentos_page = paginator_orc.get_page(page)
    
    context = {
        'vendas': vendas_page,
        'orcamentos': orcamentos_page,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'busca_nome': busca_nome,
        'tipo_filtro': tipo_filtro,
        'loja': loja
    }
    
    return render(request, 'vendas/vendas.html', context)


@AuthService.requer_login
def detalhes_venda(request, venda_id):
    """Retorna os detalhes completos de uma venda incluindo produtos"""
    try:
        # ✅ Usar novos nomes
        venda = Venda.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        ).only(
            'id', 'data_venda', 'total', 'observacao',  # ✅ Novos nomes
            'cliente__nome', 'cliente__telefone',  # ✅ Novos nomes
            'forma_pagamento__nome'  # ✅ Novo nome
        ).get(id=venda_id)  # ✅ Novo nome

        # Buscar itens
        itens = ItemVenda.objects.filter(
            venda=venda  # ✅ Novo nome
        ).select_related('produto').only(  # ✅ Novo nome
            'quantidade', 'total', 'produto__descricao'  # ✅ Novos nomes
        )

        # Montar lista de produtos
        produtos = []
        for item in itens.iterator():
            produtos.append({
                'nome': item.produto.descricao,  # ✅ Novo nome
                'quantidade': item.quantidade,  # ✅ Novo nome
                'total': f"{item.total:.2f}".replace('.', ',')  # ✅ Novo nome
            })

        # Montar dados da venda
        dados_venda = {
            'numero': f"V-{venda.id:05d}",  # ✅ Novo nome
            'cliente': venda.cliente.nome,  # ✅ Novo nome
            'telefone': venda.cliente.telefone or 'Não informado',  # ✅ Novo nome
            'data': venda.data_venda.strftime('%d/%m/%Y %H:%M'),  # ✅ Novo nome
            'total': f"{venda.total:.2f}".replace('.', ','),  # ✅ Novo nome
            'formaPagamento': venda.forma_pagamento.nome,  # ✅ Novo nome
            'produtos': produtos,
            'observacao': venda.observacao if venda.observacao else '',  # ✅ Novo nome
            'urlPdf': f"/vendas/pdf/{venda.id}/"  # ✅ Novo nome
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
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar detalhes: {str(e)}'
        }, status=500)


@AuthService.requer_login
def deletar_venda(request, venda_id):
    """Deleta uma venda do sistema"""
    if request.method == 'POST':
        try:
            venda_numero = VendaService.deletar_venda(venda_id)
            
            return JsonResponse({
                'success': True,
                'message': f'✅ Venda {venda_numero} deletada com sucesso!'
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar venda: {str(e)}'
            }, status=500)
    
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
            return JsonResponse({
                'success': False,
                'message': f'Erro ao deletar vendas: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)