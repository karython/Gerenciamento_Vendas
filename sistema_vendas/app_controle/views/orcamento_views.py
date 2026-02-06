# app_controle/views/orcamento_views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from ..services.orcamento_services import OrcamentoService
from ..models import Orcamento
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import json
import io
import os
from PIL import Image

# ✅ ADICIONAR: Funções que estavam faltando
@AuthService.requer_login
def novo_orcamento(request):
    """Página de novo orçamento"""
    loja = AuthService.loja_logada(request)
    return render(request, 'novo_orcamento.html', {'loja': loja})

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
    """Cria um novo orçamento (SEM dar baixa nos produtos)"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            print("=" * 50)
            print("[ORCAMENTO VIEW] Criando novo orçamento")
            print(f"Dados recebidos: {dados}")
            
            # Calcular subtotal dos itens e incluir frete
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
            
            print(f"[ORCAMENTO VIEW] Orçamento criado com sucesso! ID: {orcamento.idORCAMENTO}")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': 'Orçamento realizado com sucesso!',
                'orcamento_id': orcamento.idORCAMENTO
            })
            
        except ValueError as e:
            print(f"[ORCAMENTO VIEW] Erro de validação: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[ORCAMENTO VIEW] Erro ao criar orçamento: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Erro ao criar orçamento: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

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
    
    return render(request, 'orcamentos.html', context)

@AuthService.requer_login
def deletar_orcamento(request, orcamento_id):
    """Deleta um orçamento"""
    if request.method == 'POST':
        try:
            OrcamentoService.deletar_orcamento(orcamento_id)
            return JsonResponse({'success': True, 'message': 'Orçamento deletado com sucesso!'})
        except ValueError as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@AuthService.requer_login
def gerar_pdf_orcamento(request, orcamento_id):
    """Gera e faz download do orçamento em PDF com tabela estilo Venda"""
    try:
        print(f"[PDF] Gerando PDF para orçamento #{orcamento_id}")
        orcamento = Orcamento.objects.select_related(
            'CLIENTE_idCLIENTE',
            'PAGAMENTO_idPAGAMENTO'
        ).prefetch_related('itens__PRODUTO_idPRODUTO').only(
            'idORCAMENTO', 'DT_ORCAMENTO', 'QTD_ITENS', 'VLR_SUBTOTAL', 'DESCONTO', 'VLR_FRETE',
            'VLR_TOTAL', 'OBSERVACAO', 'PARCELAMENTO', 'STATUS',
            'CLIENTE_idCLIENTE__NOME_CLIENTE', 'CLIENTE_idCLIENTE__TELEFONE', 'CLIENTE_idCLIENTE__EMAIL',
            'CLIENTE_idCLIENTE__ENDERECO__LOGRADOURO', 'CLIENTE_idCLIENTE__ENDERECO__NUMERO',
            'CLIENTE_idCLIENTE__ENDERECO__BAIRRO', 'CLIENTE_idCLIENTE__ENDERECO__CEP',
            'PAGAMENTO_idPAGAMENTO__TP_PAGAMENTO'
        ).get(idORCAMENTO=orcamento_id)
        
        loja = AuthService.loja_logada(request)
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # --- CONFIGURAÇÕES DE LAYOUT ---
        margem_esq = 40
        margem_dir = width - 40
        largura_util = margem_dir - margem_esq
        y = height - 40
        
        # Desenhar a borda externa principal
        altura_recibo = 750
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(margem_esq, height - altura_recibo - 40, largura_util, altura_recibo)
        
        # --- CABEÇALHO (LOGO E DADOS DA LOJA) ---
        altura_header = 100
        y -= altura_header
        c.rect(margem_esq, y, largura_util, altura_header)
        
        # Tenta carregar a logo
        logo_paths = [
            os.path.join(settings.BASE_DIR, 'app_controle', 'static', 'img', 'logoFundo.png'),
            os.path.join(settings.STATIC_ROOT, 'img', 'logoFundo.png') if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT else None,
            os.path.join(settings.BASE_DIR, 'static', 'img', 'logoFundo.png'),
        ]
        
        logo_encontrada = False
        for logo_path in logo_paths:
            if logo_path and os.path.exists(logo_path):
                try:
                    c.drawImage(logo_path, margem_esq + 20, y + 1, width=120, height=120, preserveAspectRatio=True)
                    print(f"[PDF] Logo carregada de: {logo_path}")
                    logo_encontrada = True
                    break
                except Exception as e:
                    print(f"[PDF] Aviso: Erro ao carregar logo de {logo_path}: {str(e)}")
        
        if not logo_encontrada:
            c.setFont("Helvetica-Bold", 18)
            c.drawString(margem_esq + 20, y + 40, loja.NOME_LOJA[:15].upper())
        
        # Dados da Loja
        c.setFont("Helvetica-Bold", 10)
        x_contato = margem_esq + (largura_util / 2) + 20
        y_contato = y + 75
        
        c.drawString(x_contato, y_contato, f"{loja.NOME_LOJA}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.TELEFONE}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.CNPJ}")
        y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.EMAIL}")
        
        # --- DADOS DO CLIENTE ---
        y -= 30
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Data:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 45, y, orcamento.DT_ORCAMENTO.strftime('%d/%m/%Y'))
        c.line(margem_esq + 40, y - 2, margem_esq + 150, y - 2)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 180, y, "Telefone:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 230, y, orcamento.CLIENTE_idCLIENTE.TELEFONE)
        c.line(margem_esq + 225, y - 2, margem_esq + 380, y - 2)
        
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Cliente:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 55, y, f"{orcamento.CLIENTE_idCLIENTE.NOME_CLIENTE} (CPF: {orcamento.CLIENTE_idCLIENTE.CPF})")
        c.line(margem_esq + 50, y - 2, margem_dir - 10, y - 2)
        
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Endereço:")
        c.setFont("Helvetica", 9)
        
        # Buscar o endereço do cliente
        endereco_text = ""
        enderecos = orcamento.CLIENTE_idCLIENTE.enderecos.all()
        if enderecos:
            endereco = enderecos.first()
            endereco_text = f"{endereco.LOGRADOURO}, {endereco.NUMERO} - {endereco.BAIRRO} - {endereco.CIDADES_idCIDADES.NOME_CIDADE}/{endereco.CIDADES_idCIDADES.UF_idUF.NOME_ESTADO} - CEP: {endereco.CEP}"
        
        c.drawString(margem_esq + 60, y, endereco_text)
        c.line(margem_esq + 60, y - 2, margem_dir - 10, y - 2)
        
        # --- TÍTULO DO DOCUMENTO ---
        y -= 30
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, "ORÇAMENTO")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y - 15, f"Nº OR-{orcamento.idORCAMENTO:05d}")
        
        # Adicionar status do orçamento
        status_map = {
            'PENDENTE': 'PENDENTE',
            'APROVADO': 'APROVADO',
            'REJEITADO': 'REJEITADO',
            'CONVERTIDO': 'CONVERTIDO EM VENDA'
        }
        status_texto = status_map.get(orcamento.STATUS, orcamento.STATUS)
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, y - 28, f"Status: {status_texto}")
        
        # ==============================================================================
        # --- TABELA DE PRODUTOS (ESTILO IGUAL AO DE VENDA) ---
        # ==============================================================================
        y -= 40
        topo_tabela = y
        
        # Definição das colunas (Posição X)
        col_qtd = margem_esq + 5
        col_desc = margem_esq + 50
        col_unit = margem_dir - 130
        col_total = margem_dir - 60
        
        # Caixa cinza do cabeçalho da tabela
        c.setFillColor(colors.lightgrey)
        c.rect(margem_esq, y - 5, largura_util, 20, fill=1, stroke=1)
        c.setFillColor(colors.black)
        
        # Textos do cabeçalho
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col_qtd, y, "Qtde")
        c.drawString(col_desc, y, "Descrição")
        c.drawString(col_unit, y, "Valor Unit.")
        c.drawString(col_total, y, "Valor Total")
        
        y -= 20 # Desce para a primeira linha de dados
        
        # Loop dos Itens
        c.setFont("Helvetica", 10)
        altura_linha = 20
        
        itens = orcamento.itens.all()
        
        if not itens:
            # Caso não tenha itens (improvável, mas evita erro visual)
            c.drawString(col_desc, y - 12, "Nenhum item adicionado.")
            c.setStrokeColor(colors.grey)
            c.line(margem_esq, y - 15, margem_dir, y - 15)
            y -= altura_linha
        else:
            for item in itens.iterator():
                # Tratamento seguro do nome do produto
                produto_obj = item.PRODUTO_idPRODUTO
                # Tenta pegar NOME_PRODUTO, se falhar pega DESCRICAO, se falhar converte obj pra string
                nome_produto = getattr(produto_obj, 'NOME_PRODUTO', getattr(produto_obj, 'DESCRICAO', str(produto_obj)))
                
                # Desenhando os valores
                c.drawString(col_qtd, y - 12, f"{float(item.QUANTIDADE):.0f}")
                c.drawString(col_desc, y - 12, str(nome_produto)[:55]) # Trunca texto longo
                c.drawString(col_unit, y - 12, f"{float(item.VLR_UNITARIO):.2f}")
                c.drawString(col_total, y - 12, f"{float(item.VLR_TOTAL):.2f}")
                
                # Linha horizontal da grade (cinza)
                c.setStrokeColor(colors.grey)
                c.line(margem_esq, y - 15, margem_dir, y - 15)
                c.setStrokeColor(colors.black) # Volta para preto
                
                y -= altura_linha

        # Linhas verticais da tabela (Grade)
        fundo_tabela = y
        
        c.line(margem_esq, topo_tabela + 15, margem_esq, fundo_tabela + 5) # Borda Esq
        c.line(margem_esq + 40, topo_tabela + 15, margem_esq + 40, fundo_tabela + 5) # Separa Qtde
        c.line(margem_dir - 140, topo_tabela + 15, margem_dir - 140, fundo_tabela + 5) # Separa Unit
        c.line(margem_dir - 70, topo_tabela + 15, margem_dir - 70, fundo_tabela + 5) # Separa Total
        c.line(margem_dir, topo_tabela + 15, margem_dir, fundo_tabela + 5) # Borda Dir
        
        # ==============================================================================
        
        # --- INFORMAÇÕES RESUMIDAS ---
        y -= 25
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Forma de Pagamento: {orcamento.PAGAMENTO_idPAGAMENTO.TP_PAGAMENTO}")
        
        # Parcelamento (se houver)
        parcelamento = getattr(orcamento, 'PARCELAMENTO', '')
        if parcelamento:
            c.drawString(margem_dir - 200, y, f"Parcelamento: {parcelamento}")

        
        # Observação (se houver)
        y -= 20
        observacao = orcamento.OBSERVACAO if getattr(orcamento, 'OBSERVACAO', None) else ''
        if observacao:
            c.setFont("Helvetica-Bold", 10)
            c.drawString(margem_esq + 10, y, "Observação:")
            y -= 15
            c.setFont("Helvetica", 9)
            max_chars = 100
            for i in range(0, len(observacao), max_chars):
                linha = observacao[i:i+max_chars]
                c.drawString(margem_esq + 10, y, linha)
                y -= 12

        # --- TOTALIZADORES ---
        y -= 30
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margem_esq + 10, y, f"Subtotal: R$ {float(orcamento.VLR_SUBTOTAL):.2f}")
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Desconto: R$ {float(orcamento.DESCONTO):.2f}")
        
        y -= 20
        c.drawString(margem_esq + 10, y, f"Frete: R$ {float(orcamento.VLR_FRETE):.2f}")
        
        y -= 25
        c.setFont("Helvetica-Bold", 14)
        
        # Caixa de destaque no Total (opcional, igual ao da Venda)
        c.rect(margem_dir - 150, y - 5, 140, 20)
       
        c.drawRightString(margem_dir - 20, y + 2, f"TOTAL: R$ {float(orcamento.VLR_TOTAL):.2f}")
        y_ass = height - altura_recibo - 40 + 80 
        
        c.line(margem_esq + 20, y_ass, margem_esq + 220, y_ass)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(margem_esq + 120, y_ass - 15, "Ass. Comprador")
        
        c.line(margem_dir - 220, y_ass, margem_dir - 20, y_ass)
        c.drawCentredString(margem_dir - 120, y_ass - 15, "Assinatura Loja")

        # --- RODAPÉ ---
        y -= 50
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(margem_esq + 10, y, "Este orçamento é válido por 30 dias a partir da data de emissão.")
        y -= 15
        c.drawString(margem_esq + 10, y, "Favor confirmar antes da realização do serviço.")
        
        c.save()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orcamento_{orcamento_id:05d}.pdf"'
        
        print(f"[PDF] PDF gerado com sucesso!")
        return response
        
    except Orcamento.DoesNotExist:
        print(f"[PDF] Orçamento não encontrado: {orcamento_id}")
        return HttpResponse('Orçamento não encontrado', status=404)
    except Exception as e:
        print(f"[PDF] Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Erro ao gerar PDF: {str(e)}', status=500)


@AuthService.requer_login
def atualizar_status_orcamento(request, orcamento_id):
    """Atualiza o status do orçamento (Aprovado, Rejeitado, Convertido)"""
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            novo_status = dados.get('status', '').upper()
            
            orcamento = Orcamento.objects.get(idORCAMENTO=orcamento_id)
            
            status_validos = ['PENDENTE', 'APROVADO', 'REJEITADO', 'CONVERTIDO']
            if novo_status not in status_validos:
                return JsonResponse({
                    'success': False,
                    'message': f'Status inválido. Use: {", ".join(status_validos)}'
                }, status=400)
            
            orcamento.STATUS = novo_status
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
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@AuthService.requer_login
def converter_orcamento_venda(request, orcamento_id):
    """Converte um orçamento em venda"""
    if request.method == 'POST':
        try:
            from ..models import Venda, ItemVenda, ItemOrcamento
            
            orcamento = Orcamento.objects.get(idORCAMENTO=orcamento_id)
            
            # Verificar se o orçamento já foi convertido
            if orcamento.STATUS == 'CONVERTIDO':
                return JsonResponse({
                    'success': False,
                    'message': 'Este orçamento já foi convertido em venda'
                }, status=400)
            
            # Criar a venda com os mesmos dados do orçamento
            venda = Venda.objects.create(
                CLIENTE_idCLIENTE=orcamento.CLIENTE_idCLIENTE,
                PAGAMENTO_idPAGAMENTO=orcamento.PAGAMENTO_idPAGAMENTO,
                QTD_VENDIDA=orcamento.QTD_ITENS,
                VLR_SUBTOTAL=orcamento.VLR_SUBTOTAL,
                DESCONTO=orcamento.DESCONTO,
                VLR_FRETE=orcamento.VLR_FRETE,
                OBSERVACAO=orcamento.OBSERVACAO,
                PARCELAMENTO=orcamento.PARCELAMENTO,
                VLR_TOTAL=orcamento.VLR_TOTAL,
                ORCAMENTO_ORIGEM=orcamento  # Rastrear origem
            )
            
            # Copiar itens do orçamento para a venda (bulk create para melhor performance)
            itens_orcamento = ItemOrcamento.objects.filter(ORCAMENTO_idORCAMENTO=orcamento).values(
                'PRODUTO_idPRODUTO_id', 'QUANTIDADE', 'VLR_UNITARIO', 'VLR_TOTAL'
            )
            
            itens_venda = [
                ItemVenda(
                    VENDA_idVENDA=venda,
                    PRODUTO_idPRODUTO_id=item['PRODUTO_idPRODUTO_id'],
                    QUANTIDADE=int(item['QUANTIDADE']),
                    VLR_UNITARIO=item['VLR_UNITARIO'],
                    VLR_TOTAL=item['VLR_TOTAL']
                )
                for item in itens_orcamento
            ]
            ItemVenda.objects.bulk_create(itens_venda)
            
            # Atualizar status do orçamento
            orcamento.STATUS = 'CONVERTIDO'
            orcamento.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Orçamento #{orcamento.idORCAMENTO} convertido em Venda #{venda.idVENDA}',
                'venda_id': venda.idVENDA,
                'orcamento_id': orcamento.idORCAMENTO
            })
            
        except Orcamento.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Orçamento não encontrado'
            }, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro ao converter orçamento: {str(e)}'
            }, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)