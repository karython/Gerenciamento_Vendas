# app_controle/views/orcamento_views.py
"""
Views de gerenciamento de orçamentos
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from ..services.orcamento_services import OrcamentoService
from ..models import Orcamento, ItemOrcamento, Venda, ItemVenda
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json
import io
import os


@AuthService.requer_login
def novo_orcamento(request):
    """Página de novo orçamento"""
    loja = AuthService.loja_logada(request)
    return render(request, 'orcamentos/novo_orcamento.html', {'loja': loja})


@AuthService.requer_login
def buscar_clientes(request):
    """API para buscar clientes (autocomplete)"""
    try:
        clientes = VendaService.listar_clientes()
        return JsonResponse({'success': True, 'clientes': clientes})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@AuthService.requer_login
def buscar_produtos(request):
    """API para buscar produtos (autocomplete)"""
    try:
        produtos = VendaService.listar_produtos()
        return JsonResponse({'success': True, 'produtos': produtos})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@AuthService.requer_login
def buscar_formas_pagamento(request):
    """API para buscar formas de pagamento"""
    try:
        formas = VendaService.listar_formas_pagamento()
        return JsonResponse({'success': True, 'formas_pagamento': formas})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@AuthService.requer_login
def criar_orcamento(request):
    """Cria um novo orçamento (SEM dar baixa no estoque)"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # Calcular totais
            subtotal = sum(item.get('valor_total', 0) for item in dados.get('itens', []))
            desconto = float(dados.get('desconto', 0))
            frete = float(dados.get('frete', 0))
            total = subtotal - desconto + frete

            # Adicionar aos dados
            dados['subtotal'] = subtotal
            dados['frete'] = frete
            dados['total'] = total
            
            # Usar o service
            orcamento = OrcamentoService.criar_orcamento(dados)
            
            return JsonResponse({
                'success': True,
                'message': 'Orçamento realizado com sucesso!',
                'orcamento_id': orcamento.id  # ✅ Novo nome
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar orçamento: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)


@AuthService.requer_login
def listar_orcamentos(request):
    """Lista todos os orçamentos com filtros"""
    filtros = {
        'cliente_nome': request.GET.get('busca_nome', ''),
        'data_inicio': request.GET.get('data_inicio', ''),
        'data_fim': request.GET.get('data_fim', ''),
        'status': request.GET.get('status', 'todos')
    }
    
    orcamentos = OrcamentoService.listar_orcamentos(filtros)
    
    context = {
        'orcamentos': orcamentos,
        'busca_nome': filtros['cliente_nome'],
        'data_inicio': filtros['data_inicio'],
        'data_fim': filtros['data_fim'],
        'status_filtro': filtros['status'],
    }
    
    return render(request, 'orcamentos/orcamentos.html', context)


@AuthService.requer_login
def deletar_orcamento(request, orcamento_id):
    """Deleta um orçamento"""
    if request.method == 'POST':
        try:
            OrcamentoService.deletar_orcamento(orcamento_id)
            return JsonResponse({
                'success': True,
                'message': 'Orçamento deletado com sucesso!'
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
def atualizar_status_orcamento(request, orcamento_id):
    """Atualiza o status do orçamento"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            novo_status = dados.get('status', '').upper()
            
            orcamento = Orcamento.objects.get(id=orcamento_id)  # ✅ Novo nome
            
            status_validos = ['PENDENTE', 'APROVADO', 'REJEITADO', 'CONVERTIDO']
            if novo_status not in status_validos:
                return JsonResponse({
                    'success': False,
                    'message': f'Status inválido. Use: {", ".join(status_validos)}'
                }, status=400)
            
            orcamento.status = novo_status  # ✅ Novo nome
            orcamento.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status atualizado para {novo_status}',
                'status': novo_status
            })
            
        except Orcamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Orçamento não encontrado'
            }, status=404)
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
def converter_orcamento_venda(request, orcamento_id):
    """Converte um orçamento em venda"""
    if request.method == 'POST':
        try:
            orcamento = Orcamento.objects.get(id=orcamento_id)  # ✅ Novo nome
            
            # Verificar se já foi convertido
            if orcamento.status == 'CONVERTIDO':  # ✅ Novo nome
                return JsonResponse({
                    'success': False,
                    'message': 'Este orçamento já foi convertido em venda'
                }, status=400)
            
            # Criar venda com dados do orçamento
            venda = Venda.objects.create(
                cliente=orcamento.cliente,  # ✅ Novo nome
                forma_pagamento=orcamento.forma_pagamento,  # ✅ Novo nome
                subtotal=orcamento.subtotal,  # ✅ Novo nome
                desconto=orcamento.desconto,  # ✅ Novo nome
                frete=orcamento.frete,  # ✅ Novo nome
                observacao=orcamento.observacao,  # ✅ Novo nome
                parcelamento=orcamento.parcelamento,  # ✅ Novo nome
                total=orcamento.total,  # ✅ Novo nome
                orcamento_origem=orcamento  # ✅ Novo nome
            )
            
            # Copiar itens (bulk create para performance)
            itens_orcamento = ItemOrcamento.objects.filter(
                orcamento=orcamento  # ✅ Novo nome
            ).values(
                'produto_id',  # ✅ Novo nome
                'quantidade',  # ✅ Novo nome
                'preco_unitario',  # ✅ Novo nome
                'total'  # ✅ Novo nome
            )
            
            itens_venda = [
                ItemVenda(
                    venda=venda,  # ✅ Novo nome
                    produto_id=item['produto_id'],  # ✅ Novo nome
                    quantidade=int(item['quantidade']),
                    preco_unitario=item['preco_unitario'],
                    total=item['total']
                )
                for item in itens_orcamento
            ]
            ItemVenda.objects.bulk_create(itens_venda)
            
            # Atualizar status do orçamento
            orcamento.status = 'CONVERTIDO'  # ✅ Novo nome
            orcamento.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Orçamento #{orcamento.id} convertido em Venda #{venda.id}',  # ✅ Novos nomes
                'venda_id': venda.id,
                'orcamento_id': orcamento.id
            })
            
        except Orcamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Orçamento não encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao converter orçamento: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)

@AuthService.requer_login
def gerar_pdf_orcamento(request, orcamento_id):
    """Gera PDF do orçamento"""
    try:
        # ✅ Buscar orçamento com novos nomes
        orcamento = Orcamento.objects.select_related(
            'cliente',  # ✅ Novo nome
            'forma_pagamento'  # ✅ Novo nome
        ).prefetch_related('itens__produto').get(id=orcamento_id)  # ✅ Novos nomes
        
        loja = AuthService.loja_logada(request)
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        margem_esq = 40
        margem_dir = width - 40
        largura_util = margem_dir - margem_esq
        y = height - 40
        
        # Borda
        altura_recibo = 750
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(margem_esq, height - altura_recibo - 40, largura_util, altura_recibo)
        
        # --- CABEÇALHO ---
        altura_header = 100
        y -= altura_header
        c.rect(margem_esq, y, largura_util, altura_header)
        
        # Logo (mesmo código da venda)
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'app_controle', 'static', 'img', 'logoFundo.png'),
            os.path.join(settings.STATIC_ROOT, 'img', 'logoFundo.png') if hasattr(settings, 'STATIC_ROOT') else None,
        ]
        
        logo_encontrada = False
        for logo_path in [p for p in logo_paths if p and os.path.exists(p)]:
            try:
                c.drawImage(logo_path, margem_esq + 20, y + 1, width=120, height=120, preserveAspectRatio=True)
                logo_encontrada = True
                break
            except:
                continue
        
        if not logo_encontrada:
            c.setFont("Helvetica-Bold", 18)
            c.drawString(margem_esq + 20, y + 40, loja.nome[:15].upper())  # ✅ Novo nome
        
        # Dados da Loja
        c.setFont("Helvetica-Bold", 10)
        x_contato = margem_esq + (largura_util / 2) + 20
        y_contato = y + 75
        
        c.drawString(x_contato, y_contato, f"{loja.nome}")  # ✅ Novo nome
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.telefone}")  # ✅ Novo nome
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.cnpj}")  # ✅ Novo nome
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.email}")  # ✅ Novo nome
        
        # --- DADOS DO CLIENTE ---
        y -= 30
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Data:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 45, y, orcamento.data_orcamento.strftime('%d/%m/%Y'))  # ✅ Novo nome
        c.line(margem_esq + 40, y - 2, margem_esq + 150, y - 2)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 180, y, "Telefone:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 230, y, orcamento.cliente.telefone)  # ✅ Novo nome
        c.line(margem_esq + 225, y - 2, margem_esq + 380, y - 2)
        
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Cliente:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 55, y, f"{orcamento.cliente.nome} (CPF: {orcamento.cliente.cpf})")  # ✅ Novos nomes
        c.line(margem_esq + 50, y - 2, margem_dir - 10, y - 2)
        
        y -= 25
        
        # Endereço
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Endereço:")
        c.setFont("Helvetica", 9)
        
        endereco_text = ""
        enderecos = orcamento.cliente.enderecos.all()  # ✅ Novo nome
        if enderecos:
            end = enderecos.first()
            endereco_text = (
                f"{end.logradouro}, {end.numero or 'S/N'} - "  # ✅ Novos nomes
                f"{end.bairro} - {end.cidade.nome}/{end.cidade.uf.sigla} - "  # ✅ Novos nomes
                f"CEP: {end.cep}"  # ✅ Novo nome
            )
        
        c.drawString(margem_esq + 60, y, endereco_text)
        c.line(margem_esq + 60, y - 2, margem_dir - 10, y - 2)
        
        # --- TÍTULO ---
        y -= 30
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, "ORÇAMENTO")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y - 15, f"Nº OR-{orcamento.id:05d}")  # ✅ Novo nome
        
        # Status
        status_map = {
            'PENDENTE': 'PENDENTE',
            'APROVADO': 'APROVADO',
            'REJEITADO': 'REJEITADO',
            'CONVERTIDO': 'CONVERTIDO EM VENDA'
        }
        status_texto = status_map.get(orcamento.status, orcamento.status)  # ✅ Novo nome
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, y - 28, f"Status: {status_texto}")
        
        # --- TABELA DE PRODUTOS ---
        y -= 50
        topo_tabela = y
        
        col_qtd = margem_esq + 5
        col_desc = margem_esq + 50
        col_unit = margem_dir - 130
        col_total = margem_dir - 60
        
        # Cabeçalho
        c.setFillColor(colors.lightgrey)
        c.rect(margem_esq, y - 5, largura_util, 20, fill=1, stroke=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col_qtd, y, "Qtde")
        c.drawString(col_desc, y, "Descrição")
        c.drawString(col_unit, y, "Valor Unit.")
        c.drawString(col_total, y, "Valor Total")
        
        y -= 20
        
        # Itens
        c.setFont("Helvetica", 10)
        altura_linha = 20
        
        itens = orcamento.itens.select_related('produto').all()  # ✅ Novos nomes
        
        for item in itens:
            c.drawString(col_qtd, y - 12, f"{float(item.quantidade):.0f}")  # ✅ Novo nome
            c.drawString(col_desc, y - 12, str(item.produto.descricao)[:55])  # ✅ Novo nome
            c.drawString(col_unit, y - 12, f"{float(item.preco_unitario):.2f}")  # ✅ Novo nome
            c.drawString(col_total, y - 12, f"{float(item.total):.2f}")  # ✅ Novo nome
            
            c.setStrokeColor(colors.grey)
            c.line(margem_esq, y - 15, margem_dir, y - 15)
            c.setStrokeColor(colors.black)
            
            y -= altura_linha

        # Linhas verticais
        fundo_tabela = y
        c.line(margem_esq, topo_tabela + 15, margem_esq, fundo_tabela + 5)
        c.line(margem_esq + 40, topo_tabela + 15, margem_esq + 40, fundo_tabela + 5)
        c.line(margem_dir - 140, topo_tabela + 15, margem_dir - 140, fundo_tabela + 5)
        c.line(margem_dir - 70, topo_tabela + 15, margem_dir - 70, fundo_tabela + 5)
        c.line(margem_dir, topo_tabela + 15, margem_dir, fundo_tabela + 5)
        
        # --- INFORMAÇÕES RESUMIDAS ---
        y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Forma de Pagamento: {orcamento.forma_pagamento.nome}")  # ✅ Novo nome
        
        if orcamento.parcelamento:  # ✅ Novo nome
            c.drawString(margem_dir - 200, y, f"Parcelamento: {orcamento.parcelamento}")
        
        # Observação
        y -= 20
        if orcamento.observacao:  # ✅ Novo nome
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margem_esq + 10, y, "Observação:")
            y -= 15
            c.setFont("Helvetica", 9)
            for i in range(0, len(orcamento.observacao), 100):
                c.drawString(margem_esq + 10, y, orcamento.observacao[i:i+100])
                y -= 12

        # --- TOTALIZADORES ---
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Subtotal: R$ {float(orcamento.subtotal):.2f}")  # ✅ Novo nome
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Desconto: R$ {float(orcamento.desconto):.2f}")  # ✅ Novo nome
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Frete: R$ {float(orcamento.frete):.2f}")  # ✅ Novo nome
        
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        c.rect(margem_dir - 150, y - 5, 140, 20)
        c.drawRightString(margem_dir - 20, y + 2, f"TOTAL: R$ {float(orcamento.total):.2f}")  # ✅ Novo nome
        
        # Assinaturas
        y_ass = height - altura_recibo - 40 + 80 
        c.line(margem_esq + 20, y_ass, margem_esq + 220, y_ass)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(margem_esq + 120, y_ass - 15, "Ass. Comprador")
        
        c.line(margem_dir - 220, y_ass, margem_dir - 20, y_ass)
        c.drawCentredString(margem_dir - 120, y_ass - 15, "Assinatura Loja")

        # Rodapé
        y -= 50
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(margem_esq + 10, y, "Este orçamento é válido por 30 dias.")
        y -= 15
        c.drawString(margem_esq + 10, y, "Favor confirmar antes da realização do serviço.")
        
        c.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{orcamento_id:05d}.pdf"'
        
        return response
        
    except Orcamento.DoesNotExist:
        return HttpResponse('Orçamento não encontrado', status=404)
    except Exception as e:
        return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)