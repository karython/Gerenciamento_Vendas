/**
 * Vendas List JavaScript
 * Lógica para listagem e gerenciamento de vendas
 */

// Dados das vendas (injected via template)
let vendasData = [];

/**
 * Inicialização quando o DOM está pronto
 */
document.addEventListener("DOMContentLoaded", function() {
    inicializarDadosVendas();
    inicializarEventListeners();
});

/**
 * Inicializa dados das vendas a partir do JSON no template
 */
function inicializarDadosVendas() {
    const dataElement = document.getElementById('vendas-data');
    if (dataElement) {
        vendasData = JSON.parse(dataElement.textContent);
        console.log('Dados de vendas carregados:', vendasData);
    }
}

/**
 * Inicializa event listeners
 */
function inicializarEventListeners() {
    // Fechar modal ao clicar fora
    const modal = document.getElementById('modal-detalhes');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                fecharModal();
            }
        });
    }
    
    // Validação de datas
    const dataFim = document.getElementById('data-fim');
    if (dataFim) {
        dataFim.addEventListener('change', function() {
            const dataInicio = document.getElementById('data-inicio').value;
            if (dataInicio && this.value && this.value < dataInicio) {
                alert('A data final não pode ser anterior à data inicial!');
                this.value = '';
            }
        });
    }
}

/**
 * Seleciona ou deseleciona todas as vendas
 */
function selecionarTodas(checkbox) {
    const checkboxes = document.querySelectorAll('.checkbox-venda');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    atualizarSelecao();
}

/**
 * Atualiza barra de seleção
 */
function atualizarSelecao() {
    const checkboxes = document.querySelectorAll('.checkbox-venda:checked');
    const quantidade = checkboxes.length;
    
    const contador = document.getElementById('contador-selecionados');
    const barra = document.getElementById('barra-selecao');
    
    if (contador) {
        contador.textContent = quantidade;
    }
    
    if (barra) {
        barra.style.display = quantidade > 0 ? 'flex' : 'none';
    }
}

/**
 * Cancela seleção
 */
function cancelarSelecao() {
    document.querySelectorAll('.checkbox-venda').forEach(cb => cb.checked = false);
    document.getElementById('selecionar-todos').checked = false;
    atualizarSelecao();
}

/**
 * Deleta venda individual
 */
function deletarVenda(vendaId, vendaNumero) {
    if (!confirm(`Tem certeza que deseja deletar a venda ${vendaNumero}?\n\nEsta ação não pode ser desfeita!`)) {
        return;
    }
    
    console.log('Deletando venda ID:', vendaId);
    
    fetch(`/vendas/deletar/${vendaId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Erro: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao deletar venda. Tente novamente.');
    });
}

/**
 * Deleta múltiplas vendas
 */
async function deletarSelecionadas() {
    const checkboxes = document.querySelectorAll('.checkbox-venda:checked');
    const vendasIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (vendasIds.length === 0) {
        alert('Nenhuma venda selecionada!');
        return;
    }
    
    if (!confirm(`Tem certeza que deseja deletar ${vendasIds.length} venda(s)?\n\nEsta ação não pode ser desfeita!`)) {
        return;
    }
    
    console.log(`Deletando ${vendasIds.length} vendas...`);
    
    let deletadas = 0;
    let erros = [];
    
    for (const vendaId of vendasIds) {
        try {
            const response = await fetch(`/vendas/deletar/${vendaId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                deletadas++;
                console.log(`Venda ${vendaId} deletada`);
            } else {
                erros.push(`Venda ${vendaId}: ${data.message}`);
            }
        } catch (error) {
            erros.push(`Venda ${vendaId}: ${error.message}`);
        }
        
        // Delay entre cada operação
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    if (erros.length > 0) {
        alert(`Resultado:\n\n${deletadas} venda(s) deletada(s)\n${erros.length} erro(s):\n\n${erros.join('\n')}`);
    } else {
        alert(`Todas as ${deletadas} venda(s) foram deletadas!`);
    }
    
    location.reload();
}

/**
 * Exibe detalhes da venda em modal
 */
function verDetalhes(vendaId) {
    const id = parseInt(vendaId);
    const venda = vendasData.find(v => v.id === id);
    
    if (!venda) {
        console.error('Venda não encontrada:', vendaId);
        return;
    }
    
    // Construir tabela de itens
    let itensHtml = `
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px;">
            <thead style="background: #f8f9fa;">
                <tr>
                    <th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: left;">Produto</th>
                    <th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: center;">Qtd</th>
                    <th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: right;">Total</th>
                </tr>
            </thead>
            <tbody>
    `;

    if (venda.itens && venda.itens.length > 0) {
        venda.itens.forEach(item => {
            itensHtml += `
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">${item.produto}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">${item.qtd}</td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">R$ ${item.total}</td>
                </tr>
            `;
        });
    } else {
        itensHtml += `
            <tr>
                <td colspan="3" style="padding: 8px; text-align: center; color: #999;">Nenhum item encontrado</td>
            </tr>
        `;
    }

    itensHtml += '</tbody></table>';

    const html = `
        <div class="detalhes-venda">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p><strong>Nº Venda:</strong> ${venda.idFormatado}</p>
                    ${venda.orcamentoOrigem ? `<p><strong>Nº Orçamento:</strong> <span style="background: #e7f3ff; color: #0066cc; padding: 2px 6px; border-radius: 3px;">${venda.orcamentoOrigem}</span></p>` : ''}
                    <p><strong>Cliente:</strong> ${venda.cliente}</p>
                    <p><strong>CPF:</strong> ${venda.cpf}</p>
                    <p><strong>Telefone:</strong> ${venda.telefone}</p>
                </div>
                <div style="text-align: right;">
                    <p><strong>Data:</strong> ${venda.data}</p>
                </div>
            </div>
            
            <hr>
            <h4>Itens da Venda:</h4>
            ${itensHtml}
            
            <hr>
            <p style="font-size: 1.2em; text-align: right;"><strong>Total: R$ ${venda.valorTotal}</strong></p>
            <p style="font-size: 0.9em;"><strong>Subtotal:</strong> R$ ${venda.subtotal}</p>
            <p style="font-size: 0.9em;"><strong>Desconto:</strong> R$ ${venda.desconto}</p>
            <p style="font-size: 0.9em;"><strong>Frete:</strong> R$ ${venda.frete}</p>
            <hr>
            <p style="font-size: 0.9em;"><strong>Observação:</strong> ${venda.observacao ? venda.observacao : '<span style="color:#666">(Nenhuma)</span>'}</p>
            <p style="font-size: 0.9em;"><strong>Forma de Pagamento:</strong> ${venda.formaPagamento}</p>
            
            <div style="text-align: center; margin-top: 20px;">
                <a href="${venda.urlPdf}" class="btn-download" target="_blank">
                    <i class="fas fa-file-pdf"></i> Baixar PDF
                </a>
            </div>
        </div>
    `;
    
    const modalContent = document.getElementById('modal-content');
    if (modalContent) {
        modalContent.innerHTML = html;
    }
    
    const modal = document.getElementById('modal-detalhes');
    if (modal) {
        modal.style.display = 'flex';
    }
}

/**
 * Fecha o modal de detalhes
 */
function fecharModal() {
    const modal = document.getElementById('modal-detalhes');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Limpa filtros e recarrega página
 */
function limparFiltros() {
    window.location.href = window.location.pathname;
}

/**
 * Obtém CSRF token
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Expor funções globalmente
window.vendasList = {
    selecionarTodas,
    atualizarSelecao,
    cancelarSelecao,
    deletarVenda,
    deletarSelecionadas,
    verDetalhes,
    fecharModal,
    limparFiltros,
    getCookie
};

