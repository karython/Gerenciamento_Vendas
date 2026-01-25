# ============================================
# app_controle/views/novavenda_views.py
# ============================================

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from ..services.venda_services import VendaService
from ..services.auth_services import AuthService
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io
import os
from PIL import Image

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
    """Gera e faz download da nota fiscal em PDF no modelo de Recibo de Venda"""
    try:
        print(f"[PDF] Gerando nota fiscal para venda #{venda_id}")
        venda = VendaService.buscar_venda(venda_id)
        loja = AuthService.loja_logada(request)
        
        # Tente buscar os itens da venda (ADAPTAR PARA O SEU MODELO)
        # Exemplo: itens = venda.itemvenda_set.all() ou ItemService.listar(venda_id)
        # Se não tiver itens detalhados, criaremos uma lista fictícia com 1 item geral
        try:
            itens = venda.itens_set.all() # Ajuste aqui conforme seu relacionamento Django
        except:
            itens = [] 

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # --- CONFIGURAÇÕES DE LAYOUT ---
        margem_esq = 40
        margem_dir = width - 40
        largura_util = margem_dir - margem_esq
        y = height - 40  # Cursor vertical inicial
        
        # Desenhar a borda externa principal (O "papel" do recibo)
        # Vamos fazer um retângulo grande para conter tudo
        altura_recibo = 750 # Ajuste conforme necessidade
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(margem_esq, height - altura_recibo - 40, largura_util, altura_recibo)
        
        # --- CABEÇALHO (LOGO E DADOS DA LOJA) ---
        # Caixa do cabeçalho
        altura_header = 100
        y -= altura_header
        c.rect(margem_esq, y, largura_util, altura_header)
        
        # Lado Esquerdo: LOGO (Imagem)
        # Tenta múltiplos caminhos para encontrar a logo
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
            # Fallback: desenhar o nome da loja se a imagem não for encontrada
            print(f"[PDF] Aviso: Logo não encontrada em nenhum dos caminhos:")
            for path in logo_paths:
                if path:
                    print(f"     - {path}")
            c.setFont("Helvetica-Bold", 18)
            c.drawString(margem_esq + 20, y + 40, loja.NOME_LOJA[:15].upper())
        
        # Lado Direito: Contatos da Loja
        c.setFont("Helvetica-Bold", 10)
        x_contato = margem_esq + (largura_util / 2) + 20
        y_contato = y + 75
        
        c.drawString(x_contato, y_contato, f"{loja.NOME_LOJA}") # Usando CNPJ como identificador local
        y_contato -= 15

        # Ícones simulados com texto (ex: (W) para WhatsApp)
        c.drawString(x_contato, y_contato, f"{loja.TELEFONE}") 
        y_contato -= 15
        # Se tiver instagram no objeto loja, use aqui
        #instagram = getattr(loja, 'INSTAGRAM', '@seuinsta') 
        #c.drawString(x_contato, y_contato, f"(I) {instagram}")
        #y_contato -= 15
        c.drawString(x_contato, y_contato, f"{loja.CNPJ}") # Usando CNPJ como identificador local
        y_contato -= 15

        c.drawString(x_contato, y_contato, f"{loja.EMAIL}") # Usando CNPJ como identificador local
        y_contato -= 15
        # Endereço (quebra simples se for longo)
        endereco_loja = "DF 290, setor Sul Gama - Pte. Alta Norte, Brasília - DF" # Substitua por loja.ENDERECO se existir
        c.setFont("Helvetica", 9)
        c.drawString(x_contato, y_contato, endereco_loja[:40])

        # --- DADOS DO CLIENTE (Bloco estilo formulário) ---
        y -= 30 # Espaço
        
        # Linha 1: Data e Telefone
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Data:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 45, y, venda.DT_VENDA.strftime('%d/%m/%Y'))
        c.line(margem_esq + 40, y - 2, margem_esq + 150, y - 2) # Linha sublinhada
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 180, y, "Telefone:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 230, y, venda.CLIENTE_idCLIENTE.TELEFONE)
        c.line(margem_esq + 225, y - 2, margem_esq + 380, y - 2)
        
        # Checkbox WhatsApp (Simulado)
        c.rect(margem_dir - 60, y, 10, 10) 
        c.setFont("Helvetica", 8)
        c.drawString(margem_dir - 45, y+2, "WhatsApp")
        
        y -= 25
        
        # Linha 2: Cliente
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Cliente:")
        c.setFont("Helvetica", 10)
        c.drawString(margem_esq + 55, y, f"{venda.CLIENTE_idCLIENTE.NOME_CLIENTE} (CPF: {venda.CLIENTE_idCLIENTE.CPF})")
        c.line(margem_esq + 50, y - 2, margem_dir - 10, y - 2)
        
        y -= 25
        
        # Linha 3: Endereço (Se tiver no cliente, adicione aqui)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margem_esq + 10, y, "Endereço:")
        c.line(margem_esq + 60, y - 2, margem_dir - 10, y - 2)
        
        y -= 10
        
        # --- TÍTULO DO RECIBO ---
        y -= 30
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, y, "RECIBO DE VENDA")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, y - 15, f"Nº V-{venda.idVENDA:05d}")

        # --- TABELA DE ITENS ---
        y -= 40
        topo_tabela = y
        
        # Cabeçalhos da Tabela
        # Definição das colunas (Posição X)
        col_qtd = margem_esq + 5
        col_desc = margem_esq + 50
        col_unit = margem_dir - 130
        col_total = margem_dir - 60
        
        # Caixa do cabeçalho da tabela
        c.setFillColor(colors.lightgrey)
        c.rect(margem_esq, y - 5, largura_util, 20, fill=1, stroke=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(col_qtd, y, "Qtde")
        c.drawString(col_desc, y, "Descrição")
        c.drawString(col_unit, y, "Valor Unit.")
        c.drawString(col_total, y, "Valor")
        
        y -= 20 # Desce para a primeira linha de dados
        
        # Loop dos Itens
        # Se não houver itens na lista, criamos uma linha geral baseada no total
        if not itens:
            dados_tabela = [
                (venda.QTD_VENDIDA, "Produtos Diversos / Venda Geral", "", f"{venda.VLR_TOTAL:.2f}")
            ]
        else:
            # Aqui você adaptaria para ler os atributos do seu objeto item
            dados_tabela = []
            for item in itens:
                # Exemplo: item.quantidade, item.produto.nome, item.preco_unit, item.total
                dados_tabela.append((item.quantidade, item.descricao, f"{item.preco:.2f}", f"{item.total:.2f}"))

        # Desenhando as linhas
        c.setFont("Helvetica", 10)
        altura_linha = 20
        
        # Vamos desenhar linhas até preencher um espaço fixo ou apenas os itens
        # Para ficar igual à imagem (com linhas vazias), faríamos um loop fixo range(15)
        # Mas para nota fiscal, melhor listar só o que existe.
        
        for qtd, desc, unit, total in dados_tabela:
            c.drawString(col_qtd, y - 12, str(qtd))
            c.drawString(col_desc, y - 12, str(desc)[:55]) # Trunca texto longo
            c.drawString(col_unit, y - 12, str(unit))
            c.drawString(col_total, y - 12, str(total))
            
            # Linha horizontal da grade
            c.setStrokeColor(colors.grey)
            c.line(margem_esq, y - 15, margem_dir, y - 15)
            c.setStrokeColor(colors.black)
            
            y -= altura_linha

        # Linhas verticais da tabela (da base até o topo)
        # Fundo da tabela (onde parou o Y)
        fundo_tabela = y
        
        c.line(margem_esq, topo_tabela + 15, margem_esq, fundo_tabela + 5) # Esq
        c.line(margem_esq + 40, topo_tabela + 15, margem_esq + 40, fundo_tabela + 5) # Separa Qtde
        c.line(margem_dir - 140, topo_tabela + 15, margem_dir - 140, fundo_tabela + 5) # Separa Unit
        c.line(margem_dir - 70, topo_tabela + 15, margem_dir - 70, fundo_tabela + 5) # Separa Total
        c.line(margem_dir, topo_tabela + 15, margem_dir, fundo_tabela + 5) # Dir
        
        # --- TOTAL ---
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margem_dir - 150, y, "Total:")
        
        # Caixa do valor total
        c.rect(margem_dir - 100, y - 5, 95, 20)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(margem_dir - 10, y + 2, f"R$ {venda.VLR_TOTAL:.2f}")
        
        # --- ASSINATURAS ---
        # Posicionar assinaturas perto do fim da página/box
        y_ass = height - altura_recibo - 40 + 80 
        
        c.line(margem_esq + 20, y_ass, margem_esq + 220, y_ass)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(margem_esq + 120, y_ass - 15, "Ass. Comprador")
        
        c.line(margem_dir - 220, y_ass, margem_dir - 20, y_ass)
        c.drawCentredString(margem_dir - 120, y_ass - 15, "Assinatura Loja")
        
        # --- RODAPÉ / GARANTIA ---
        y_rodape = height - altura_recibo - 40 + 30
        c.setFont("Helvetica", 7)
        texto_garantia = "Nossos produtos têm garantia de XX dias. Não cobrimos mau uso ou danos elétricos."
        c.drawCentredString(width / 2, y_rodape, texto_garantia)
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"Recibo_V-{venda.idVENDA:05d}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        print(f"[PDF] ✅ Recibo V-{venda.idVENDA:05d} gerado com sucesso!")
        return response
        
    except Exception as e:
        print(f"[PDF] ❌ Erro ao gerar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Erro ao gerar PDF: {str(e)}", status=500)