// ============================================
// ORCAMENTOS.JS - Lógica para página de orçamentos
// ============================================

const orcamentosData = JSON.parse(document.getElementById('orcamentos-data').textContent);

function verDetalhes(id) {
    const orcamento = orcamentosData.find(o => o.id === id);
    
    if (!orcamento) return;

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

    orcamento.itens.forEach(item => {
        itensHtml += `
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #eee;">${item.produto}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: center;">${item.qtd}</td>
                <td style="padding: 8px; border-bottom: 1px solid #eee; text-align: right;">R$ ${item.total}</td>
            </tr>
        `;
    });

    itensHtml += `</tbody></table>`;

    const html = `
        <div class="detalhes-venda">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <p><strong>Nº:</strong> ${orcamento.idFormatado}</p>
                    <p><strong>Cliente:</strong> ${orcamento.cliente}</p>
                    <p><strong>Telefone:</strong> ${orcamento.telefone}</p>
                </div>
                <div style="text-align: right;">
                    <p><strong>Data:</strong> ${orcamento.data}</p>
                    <p>
                        <strong>Status:</strong>
                        <select id="status-select-${orcamento.id}" class="status-select" onchange="atualizarStatus(${orcamento.id}, this.value)">
                            <option value="PENDENTE" ${orcamento.status === 'PENDENTE' ? 'selected' : ''}>Pendente</option>
                            <option value="APROVADO" ${orcamento.status === 'APROVADO' ? 'selected' : ''}>Aprovado</option>
                            <option value="REJEITADO" ${orcamento.status === 'REJEITADO' ? 'selected' : ''}>Rejeitado</option>
                            <option value="CONVERTIDO" ${orcamento.status === 'CONVERTIDO' ? 'selected' : ''}>Convertido</option>
                        </select>
                    </p>
                </div>
            </div>
            
            <hr>
            <h4>Itens do Orçamento:</h4>
            ${itensHtml}
            
            <hr>
            <p class="text-right" style="font-size: 1.2em; text-align: right;"><strong>Total: R$ ${orcamento.total}</strong></p>
            <p style="font-size: 0.9em;"><strong>Forma Pagamento:</strong> ${orcamento.formaPagamento}</p>
            <hr>
            <p style="font-size: 0.9em;"><strong>Observação:</strong> ${orcamento.observacao ? orcamento.observacao : '<span style="color:#666">(Nenhuma)</span>'}</p>
            
            <div style="text-align: center; margin-top: 20px; display: flex; gap: 10px; justify-content: center;">
                ${orcamento.status !== 'CONVERTIDO' ? `
                    <button class="btn-download" onclick="abrirConverterModal(${orcamento.id})" style="background-color: #28a745;">
                        <i class="fas fa-exchange-alt"></i> Converter em Venda
                    </button>
                ` : '<span style="color: #666; font-weight: bold;">✓ Já foi convertido em venda</span>'}
                <a href="${orcamento.urlPdf}" class="btn-download" target="_blank">
                    <i class="fas fa-file-pdf"></i> Baixar PDF
                </a>
            </div>
        </div>
    `;
    
    document.getElementById('modal-content').innerHTML = html;
    document.getElementById('modal-detalhes').style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modal-detalhes').style.display = 'none';
}

document.getElementById('modal-detalhes').addEventListener('click', function(e) {
    if (e.target === this) fecharModal();
});

function deletarOrcamento(id) {
    if (!confirm('Tem certeza que deseja deletar este orçamento?')) return false;

    fetch(`/orcamentos/deletar/${id}/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Erro: ' + data.message);
        }
    });
}

function selecionarTodos(checkbox) {
    document.querySelectorAll('.checkbox-orcamento').forEach(cb => cb.checked = checkbox.checked);
    atualizarSelecao();
}

function atualizarSelecao() {
    const qtd = document.querySelectorAll('.checkbox-orcamento:checked').length;
    document.getElementById('contador-selecionados').textContent = qtd;
    document.getElementById('barra-selecao').style.display = qtd > 0 ? 'flex' : 'none';
}

function cancelarSelecao() {
    document.querySelectorAll('.checkbox-orcamento').forEach(cb => cb.checked = false);
    document.getElementById('selecionar-todos').checked = false;
    atualizarSelecao();
}

async function deletarSelecionados() {
    const ids = Array.from(document.querySelectorAll('.checkbox-orcamento:checked')).map(cb => cb.value);
    
    if (ids.length === 0) return;
    if (!confirm(`⚠️ Tem certeza que deseja deletar ${ids.length} orçamentos?`)) return;

    for (const id of ids) {
        await fetch(`/orcamentos/deletar/${id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') }
        });
    }
    location.reload();
}

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

let orcamentoEmConverso = null;

function abrirConverterModal(id) {
    orcamentoEmConverso = id;
    const orcamento = orcamentosData.find(o => o.id === id);
    
    if (!orcamento) return;
    
    document.getElementById('converter-info').innerHTML = `
        <strong>Nº do Orçamento:</strong> ${orcamento.idFormatado}<br>
        <strong>Cliente:</strong> ${orcamento.cliente}<br>
        <strong>Valor Total:</strong> R$ ${orcamento.total}
    `;
    
    document.getElementById('modal-converter').style.display = 'flex';
}

function fecharModalConverter() {
    document.getElementById('modal-converter').style.display = 'none';
    orcamentoEmConverso = null;
}

async function confirmarConversao() {
    if (!orcamentoEmConverso) return;
    
    const btn = document.getElementById('btn-converter-confirmar');
    btn.disabled = true;
    btn.textContent = 'Convertendo...';
    
    try {
        const response = await fetch(`/orcamentos/converter/${orcamentoEmConverso}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ ${data.message}`);
            location.reload();
        } else {
            alert(`❌ Erro: ${data.message}`);
        }
    } catch (error) {
        alert(`❌ Erro na conversão: ${error.message}`);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Converter para Venda';
        fecharModalConverter();
    }
}

async function atualizarStatus(orcamentoId, novoStatus) {
    if (!confirm(`Alterar status para ${novoStatus}?`)) return;
    
    try {
        const response = await fetch(`/orcamentos/status/${orcamentoId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ status: novoStatus })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ ${data.message}`);
            location.reload();
        } else {
            alert(`❌ Erro: ${data.message}`);
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
    }
}