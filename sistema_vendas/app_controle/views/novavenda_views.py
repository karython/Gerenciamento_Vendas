# ============================================
# app_controle/views/novavenda_views.py
# ============================================

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

@AuthService.requer_login
def nova_venda(request):
    """Página de nova venda"""
    loja = AuthService.loja_logada(request)
    return render(request, 'nova_venda.html', {'loja': loja})

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
            import json
            dados = json.loads(request.body)
            
            print("=" * 50)
            print("[VIEW] Criando nova venda")
            print(f"Dados recebidos: {dados}")
            
            if not dados.get('cliente_id'):
                return JsonResponse({'success': False, 'message': 'Selecione um cliente'}, status=400)
            
            if not dados.get('itens') or len(dados['itens']) == 0:
                return JsonResponse({'success': False, 'message': 'Adicione pelo menos um produto'}, status=400)
            
            if not dados.get('forma_pagamento_id'):
                return JsonResponse({'success': False, 'message': 'Selecione uma forma de pagamento'}, status=400)
            
            venda = VendaService.criar_venda(dados)
            
            print(f"[VIEW] Venda criada com sucesso! ID: {venda.idVENDA}")
            print("=" * 50)
            
            return JsonResponse({
                'success': True,
                'message': 'Venda realizada com sucesso!',
                'venda_id': venda.idVENDA
            })
            
        except ValueError as e:
            print(f"[VIEW] Erro de validação: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
        except Exception as e:
            print(f"[VIEW] Erro ao criar venda: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Erro ao criar venda: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

@AuthService.requer_login
def gerar_pdf_venda(request, venda_id):
    """Gera e faz download da nota fiscal em PDF"""
    try:
        print(f"[PDF] Gerando nota fiscal para venda #{venda_id}")
        venda = VendaService.buscar_venda(venda_id)
        loja = AuthService.loja_logada(request)
        
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        y = height - 50
        
        # CABEÇALHO
        pdf.setFont("Helvetica-Bold", 24)
        pdf.drawString(50, y, "NOTA FISCAL DE VENDA")
        y -= 30
        
        # Dados da Loja
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, f"Loja: {loja.NOME_LOJA}")
        y -= 15
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"CNPJ: {loja.CNPJ}")
        y -= 30
        
        # ID da Venda
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, f"Nota Fiscal Nº: V-{venda.idVENDA:05d}")
        y -= 25
        
        # Data
        pdf.setFont("Helvetica", 11)
        pdf.drawString(50, y, f"Data: {venda.DT_VENDA.strftime('%d/%m/%Y às %H:%M')}")
        y -= 40
        
        # INFORMAÇÕES DO CLIENTE
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "DADOS DO CLIENTE")
        y -= 20
        
        pdf.setFont("Helvetica", 10)
        pdf.drawString(70, y, f"Nome: {venda.CLIENTE_idCLIENTE.NOME_CLIENTE}")
        y -= 15
        pdf.drawString(70, y, f"CPF/CNPJ: {venda.CLIENTE_idCLIENTE.CPF}")
        y -= 15
        pdf.drawString(70, y, f"Telefone: {venda.CLIENTE_idCLIENTE.TELEFONE}")
        y -= 35
        
        # FORMA DE PAGAMENTO
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, f"Forma de Pagamento: {venda.PAGAMENTO_idPAGAMENTO.TP_PAGAMENTO}")
        y -= 35
        
        # LINHA SEPARADORA
        pdf.line(50, y, width - 50, y)
        y -= 30
        
        # VALORES
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "RESUMO DO PAGAMENTO")
        y -= 25
        
        pdf.setFont("Helvetica", 11)
        pdf.drawString(70, y, f"Quantidade de Itens: {venda.QTD_VENDIDA}")
        y -= 20
        
        pdf.drawString(70, y, f"Valor Total:")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(350, y, f"R$ {venda.VLR_TOTAL:.2f}")
        y -= 40
        
        # LINHA SEPARADORA
        pdf.setFont("Helvetica", 10)
        pdf.line(50, y, width - 50, y)
        y -= 30
        
        # ASSINATURA
        pdf.drawString(50, y, "_" * 40)
        y -= 15
        pdf.drawString(50, y, "Assinatura do Cliente")
        
        # RODAPÉ
        pdf.setFont("Helvetica", 8)
        pdf.drawString(50, 40, "Sistema de Gerenciamento de Vendas")
        pdf.drawString(50, 30, f"Documento gerado em {venda.DT_VENDA.strftime('%d/%m/%Y às %H:%M')}")
        pdf.drawString(width - 150, 40, f"Venda: V-{venda.idVENDA:05d}")
        
        pdf.showPage()
        pdf.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="NotaFiscal_V-{venda.idVENDA:05d}.pdf"'
        
        print(f"[PDF] ✅ Nota fiscal V-{venda.idVENDA:05d} gerada com sucesso!")
        
        return response
        
    except Exception as e:
        print(f"[PDF] ❌ Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)