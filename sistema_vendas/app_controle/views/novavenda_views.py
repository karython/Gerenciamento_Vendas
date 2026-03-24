# app_controle/views/novavenda_views.py
"""
Views para criação de novas vendas
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from ..models import Venda, ItemVenda
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import json
import io
import os


@AuthService.requer_login
def nova_venda(request):
    """Página de nova venda"""
    loja = AuthService.loja_logada(request)
    return render(request, 'vendas/nova_venda.html', {'loja': loja})


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
def criar_venda(request):
    """Cria uma nova venda"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # Validações
            if not dados.get('cliente_id'):
                return JsonResponse({
                    'success': False,
                    'message': 'Selecione um cliente'
                }, status=400)
            
            if not dados.get('itens') or len(dados['itens']) == 0:
                return JsonResponse({
                    'success': False,
                    'message': 'Adicione pelo menos um produto'
                }, status=400)
            
            if not dados.get('forma_pagamento_id'):
                return JsonResponse({
                    'success': False,
                    'message': 'Selecione uma forma de pagamento'
                }, status=400)
            
            # Calcular totais
            subtotal = sum(item.get('valor_total', 0) for item in dados.get('itens', []))
            desconto = float(dados.get('desconto', 0))
            frete = float(dados.get('frete', 0))
            total = subtotal - desconto + frete

            # Adicionar aos dados
            dados['subtotal'] = subtotal
            dados['frete'] = frete
            dados['total'] = total
            
            # Criar venda
            venda = VendaService.criar_venda(dados)
            
            return JsonResponse({
                'success': True,
                'message': 'Venda realizada com sucesso!',
                'venda_id': venda.id  # ✅ Novo nome
            })
            
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao criar venda: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'message': 'Método não permitido'
    }, status=405)

@AuthService.requer_login
def gerar_pdf_venda(request, venda_id):
    """Gera PDF do recibo de venda"""
    try:
        venda = Venda.objects.select_related(
            'cliente',
            'forma_pagamento'
        ).prefetch_related('itens__produto').get(id=venda_id)
        
        loja = AuthService.loja_logada(request)
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        margem_esq = 40
        margem_dir = width - 40
        largura_util = margem_dir - margem_esq
        y = height - 40
        
        # Borda externa
        altura_recibo = 750
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(margem_esq, height - altura_recibo - 40, largura_util, altura_recibo)
        
        # --- CABEÇALHO ---
        altura_header = 100
        y -= altura_header
        c.rect(margem_esq, y, largura_util, altura_header)
        
        # Logo
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
            c.drawString(margem_esq + 20, y + 40, loja.nome[:15].upper())
        
        # Dados da Loja
        c.setFont("Helvetica-Bold", 10)
        x_contato = margem_esq + (largura_util / 2) + 20
        y_contato = y + 75
        
        c.drawString(x_contato, y_contato, f"{loja.nome}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.telefone}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.cnpj}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.email}")
        
        # --- DADOS DO CLIENTE ---
        y -= 30
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Data:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 45, y, venda.data_venda.strftime('%d/%m/%Y'))
        c.line(margem_esq + 40, y - 2, margem_esq + 150, y - 2)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 180, y, "Telefone:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 230, y, venda.cliente.telefone)
        c.line(margem_esq + 225, y - 2, margem_esq + 380, y - 2)
        
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Cliente:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 55, y, f"{venda.cliente.nome} (CPF: {venda.cliente.cpf})")
        c.line(margem_esq + 50, y - 2, margem_dir - 10, y - 2)
        
        y -= 25
        
        # Endereço
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Endereço:")
        c.setFont("Helvetica", 9)
        
        endereco_text = ""
        enderecos = venda.cliente.enderecos.all()
        if enderecos:
            end = enderecos.first()
            endereco_text = (
                f"{end.logradouro}, {end.numero or 'S/N'} - "
                f"{end.bairro} - {end.cidade.nome}/{end.cidade.uf.sigla} - "
                f"CEP: {end.cep}"
            )
        
        c.drawString(margem_esq + 60, y, endereco_text)
        c.line(margem_esq + 60, y - 2, margem_dir - 10, y - 2)
        
        # --- TÍTULO ---
        y -= 30
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, "RECIBO DE VENDA")
        c.setFont("Helvetica", 10)
        
        numero_venda = f"Nº V-{venda.id:05d}"
        if venda.orcamento_origem:
            numero_venda += f" | Orçamento: OR-{venda.orcamento_origem.id:05d}"
        
        c.drawCentredString(width / 2, y - 15, numero_venda)
        
        # --- TABELA DE PRODUTOS ---
        y -= 40
        topo_tabela = y
        
        col_qtd = margem_esq + 5
        col_desc = margem_esq + 50
        col_unit = margem_dir - 130
        col_total = margem_dir - 60
        
        # Cabeçalho da tabela
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
        
        itens = venda.itens.select_related('produto').all()
        
        for item in itens:
            c.drawString(col_qtd, y - 12, f"{int(item.quantidade)}")
            c.drawString(col_desc, y - 12, str(item.produto.descricao)[:55])
            c.drawString(col_unit, y - 12, f"{float(item.preco_unitario):.2f}")
            c.drawString(col_total, y - 12, f"{float(item.total):.2f}")
            
            c.setStrokeColor(colors.grey)
            c.line(margem_esq, y - 15, margem_dir, y - 15)
            c.setStrokeColor(colors.black)
            
            y -= altura_linha

        # Linhas verticais da tabela
        fundo_tabela = y
        c.line(margem_esq, topo_tabela + 15, margem_esq, fundo_tabela + 5)
        c.line(margem_esq + 40, topo_tabela + 15, margem_esq + 40, fundo_tabela + 5)
        c.line(margem_dir - 140, topo_tabela + 15, margem_dir - 140, fundo_tabela + 5)
        c.line(margem_dir - 70, topo_tabela + 15, margem_dir - 70, fundo_tabela + 5)
        c.line(margem_dir, topo_tabela + 15, margem_dir, fundo_tabela + 5)
        
        # --- INFORMAÇÕES DE PAGAMENTO ---
        y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Forma de Pagamento: {venda.forma_pagamento.nome}")
        
        if venda.parcelamento:
            c.drawString(margem_dir - 200, y, f"Parcelamento: {venda.parcelamento}")
        
        # Observação
        y -= 20
        if venda.observacao:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margem_esq + 10, y, "Observação:")
            y -= 15
            c.setFont("Helvetica", 9)
            for i in range(0, len(venda.observacao), 100):
                c.drawString(margem_esq + 10, y, venda.observacao[i:i+100])
                y -= 12

        # --- TOTALIZADORES ---
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Subtotal: R$ {float(venda.subtotal):.2f}")
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Desconto: R$ {float(venda.desconto):.2f}")
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Frete: R$ {float(venda.frete):.2f}")
        
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        # ✅ Retângulo removido
        c.drawRightString(margem_dir - 20, y + 2, f"TOTAL: R$ {float(venda.total):.2f}")
        
        # --- ASSINATURAS (✅ posição dinâmica, sempre abaixo dos totalizadores) ---
        y -= 60
        c.line(margem_esq + 20, y, margem_esq + 220, y)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(margem_esq + 120, y - 15, "Ass. Comprador")
        
        c.line(margem_dir - 220, y, margem_dir - 20, y)
        c.drawCentredString(margem_dir - 120, y - 15, "Assinatura Loja")

        # --- RODAPÉ ---
        y -= 40
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(margem_esq + 10, y, "Obrigado pela preferência!")
        
        c.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="venda_{venda_id:05d}.pdf"'
        
        return response
        
    except Venda.DoesNotExist:
        return HttpResponse('Venda não encontrada', status=404)
    except Exception as e:
        return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)