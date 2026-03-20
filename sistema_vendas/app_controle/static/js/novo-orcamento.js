/**
 * Novo Orçamento JavaScript
 * Lógica para criação de novos orçamentos
 */

// Variáveis globais
let itensOrcamento = [];
let produtosDisponiveis = [];

/**
 * Inicialização quando o DOM está pronto
 */
document.addEventListener("DOMContentLoaded", function() {
    inicializarEventListeners();
    carregarClientes();
    carregarProdutos();
    carregarFormasPagamento();
    inicializarMascarasMoeda();
    inicializarContadorObservacao();
});

/**
 * Inicializa event listeners para botões e formulários
 */
function inicializarEventListeners() {
    const btnAdicionar = document.getElementById('btn-adicionar');
    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', adicionarItem);
    }

    const formOrcamento = document.getElementById('form-novo-orcamento');
    if (formOrcamento) {
        formOrcamento.addEventListener('submit', finalizarOrcamento);
    }
}

/**
 * Carrega lista de clientes do banco
 */
async function carregarClientes() {
    try {
        const response = await fetch(window.urls.buscarClientes);
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('cliente');
            select.innerHTML = '<option value="">Selecione um cliente...</option>';

            data.clientes.forEach(cliente => {
                const option = document.createElement('option');
                option.value = cliente.id;
                option.textContent = cliente.label;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar clientes:', error);
    }
}

/**
 * Carrega lista de produtos do estoque e inicializa autocomplete
 */
async function carregarProdutos() {
    try {
        const response = await fetch(window.urls.buscarProdutos);
        const data = await response.json();

        if (data.success) {
            produtosDisponiveis = data.produtos;
            inicializarAutocompleteProduto();
        }
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
    }
}

/**
 * Inicializa o campo de autocomplete de produto
 */
function inicializarAutocompleteProduto() {
    const input    = document.getElementById('produto-input');
    const hidden   = document.getElementById('produto');
    const dropdown = document.getElementById('produto-dropdown');
    let highlightIdx   = -1;
    let filtradosAtual = [];

    function renderDropdown(lista) {
        filtradosAtual = lista;
        highlightIdx   = -1;
        dropdown.innerHTML = '';

        if (lista.length === 0) {
            dropdown.style.display = 'none';
            return;
        }

        lista.forEach((produto, idx) => {
            const li = document.createElement('li');
            li.textContent = produto.label;
            li.dataset.idx = idx;
            li.style.cssText = 'padding: 10px 14px; cursor: pointer; border-bottom: 1px solid #f0f0f0; font-size: 0.95em;';

            li.addEventListener('mouseenter', () => {
                removeAllHighlights();
                highlightIdx = idx;
                li.style.background = '#f0f4ff';
            });
            li.addEventListener('mouseleave', () => {
                li.style.background = '';
            });
            li.addEventListener('mousedown', (e) => {
                e.preventDefault(); // evita blur antes do click
                selecionarProduto(produto);
            });

            dropdown.appendChild(li);
        });

        dropdown.style.display = 'block';
    }

    function removeAllHighlights() {
        dropdown.querySelectorAll('li').forEach(li => li.style.background = '');
    }

    function selecionarProduto(produto) {
        hidden.value = produto.id;
        hidden.dataset.valor     = produto.valor;
        hidden.dataset.estoque   = produto.estoque;
        hidden.dataset.descricao = produto.descricao;
        hidden.dataset.isService = produto.is_service;

        input.value = produto.label;
        dropdown.style.display = 'none';
        highlightIdx = -1;

        // Foca na quantidade para agilizar o fluxo
        document.getElementById('quantidade').focus();
    }

    function filtrar(texto) {
        if (!texto.trim()) {
            renderDropdown([]);
            return;
        }
        const termo = texto.toLowerCase();
        const filtrados = produtosDisponiveis.filter(p =>
            p.label.toLowerCase().includes(termo) ||
            String(p.id).includes(termo)
        );
        renderDropdown(filtrados);
    }

    // Digitar → filtrar e limpar seleção anterior
    input.addEventListener('input', () => {
        hidden.value = '';
        filtrar(input.value);
    });

    // Abrir dropdown ao focar se já houver texto
    input.addEventListener('focus', () => {
        if (input.value.trim()) filtrar(input.value);
    });

    // Fechar ao clicar fora
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });

    // Navegação por teclado
    input.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('li');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            highlightIdx = Math.min(highlightIdx + 1, items.length - 1);
            removeAllHighlights();
            if (items[highlightIdx]) items[highlightIdx].style.background = '#f0f4ff';

        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightIdx = Math.max(highlightIdx - 1, 0);
            removeAllHighlights();
            if (items[highlightIdx]) items[highlightIdx].style.background = '#f0f4ff';

        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlightIdx >= 0 && filtradosAtual[highlightIdx]) {
                selecionarProduto(filtradosAtual[highlightIdx]);
            }

        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
}

/**
 * Carrega formas de pagamento
 */
async function carregarFormasPagamento() {
    try {
        const response = await fetch(window.urls.buscarFormasPagamento);
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('forma-pagamento');
            data.formas_pagamento.forEach(forma => {
                const option = document.createElement('option');
                option.value = forma.id;
                option.textContent = forma.tipo;
                option.dataset.tipo = forma.tipo.toLowerCase();
                select.appendChild(option);
            });

            select.addEventListener('change', function() {
                const selectedOption    = this.options[this.selectedIndex];
                const tipoForma         = selectedOption.dataset.tipo;
                const parcelamentoGrupo = document.getElementById('parcelamento-grupo');

                if (tipoForma && (tipoForma.includes('cartão de crédito') || tipoForma.includes('crédito'))) {
                    parcelamentoGrupo.style.display = 'block';
                } else {
                    parcelamentoGrupo.style.display = 'none';
                }
            });
        }
    } catch (error) {
        console.error('Erro ao carregar formas de pagamento:', error);
    }
}

/**
 * Adiciona item ao orçamento
 */
function adicionarItem() {
    const hidden          = document.getElementById('produto');
    const inputTexto      = document.getElementById('produto-input');
    const quantidadeInput = document.getElementById('quantidade');

    const produtoId  = hidden.value;
    const quantidade = parseInt(quantidadeInput.value);

    if (!produtoId) {
        alert('Selecione um produto da lista');
        return;
    }
    if (!quantidade || quantidade < 1) {
        alert('Informe uma quantidade válida');
        return;
    }

    const estoque   = parseInt(hidden.dataset.estoque);
    const isService = hidden.dataset.isService === 'true';

    if (!isService && quantidade > estoque) {
        alert(`Estoque insuficiente! Disponível: ${estoque} unidades`);
        return;
    }

    const itemExistente = itensOrcamento.find(item => item.produto_id === parseInt(produtoId));
    if (itemExistente) {
        alert('Produto já adicionado! Remova-o primeiro para alterar a quantidade.');
        return;
    }

    let valorUnitario = parseFloat(hidden.dataset.valor);

    if (isService) {
        const input = prompt('Produto serviço: informe o valor unitário (use vírgula ou ponto):', hidden.dataset.valor);
        if (input === null) return;
        const normalized = String(input).replace(/\s+/g, '').replace(/,/g, '.');
        valorUnitario = parseFloat(normalized);
        if (isNaN(valorUnitario) || valorUnitario <= 0) {
            alert('Valor inválido para o serviço');
            return;
        }
    }

    const valorTotal = quantidade * valorUnitario;

    itensOrcamento.push({
        produto_id:     parseInt(produtoId),
        descricao:      hidden.dataset.descricao,
        quantidade:     quantidade,
        valor_unitario: valorUnitario,
        valor_total:    valorTotal
    });

    atualizarTabelaItens();

    // Limpar campos
    hidden.value          = '';
    inputTexto.value      = '';
    quantidadeInput.value = 1;
    inputTexto.focus();
}

/**
 * Atualiza tabela de itens do orçamento
 */
function atualizarTabelaItens() {
    const tbody = document.getElementById('itens-orcamento');

    if (itensOrcamento.length === 0) {
        tbody.innerHTML = '<tr id="linha-vazia"><td colspan="5" style="text-align: center; padding: 20px; color: #777;">Nenhum item adicionado</td></tr>';
        document.getElementById('subtotal').textContent = 'R$ 0,00';
        document.getElementById('total').textContent = 'R$ 0,00';
        return;
    }

    tbody.innerHTML = '';
    let subtotal = 0;

    itensOrcamento.forEach((item, index) => {
        subtotal += item.valor_total;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.descricao}</td>
            <td style="text-align: center;">${item.quantidade}</td>
            <td>R$ ${item.valor_unitario.toFixed(2)}</td>
            <td>R$ ${item.valor_total.toFixed(2)}</td>
            <td style="text-align: center;">
                <button type="button" class="btn-acao btn-deletar btn-remover" data-index="${index}" title="Remover Item">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.btn-remover').forEach(btn => {
        btn.addEventListener('click', function() {
            removerItem(parseInt(this.dataset.index));
        });
    });

    document.getElementById('subtotal').textContent = `R$ ${subtotal.toFixed(2)}`;
    calcularTotal();
}

/**
 * Remove item do orçamento
 */
function removerItem(index) {
    itensOrcamento.splice(index, 1);
    atualizarTabelaItens();
}

/**
 * Calcula total com desconto e frete
 */
function calcularTotal() {
    const subtotal = itensOrcamento.reduce((sum, item) => sum + item.valor_total, 0);
    const desconto = parseCurrencyToFloat(document.getElementById('desconto').value) || 0;
    const frete    = parseCurrencyToFloat(document.getElementById('frete').value) || 0;
    const total    = subtotal - desconto + frete;

    document.getElementById('total').textContent = `R$ ${total.toFixed(2)}`;
}

/**
 * Inicializa máscaras de moeda
 */
function inicializarMascarasMoeda() {
    attachCurrencyMask('desconto');
    attachCurrencyMask('frete');
}

/**
 * Aplica máscara de moeda a um campo
 */
function attachCurrencyMask(selector) {
    const el = document.getElementById(selector);
    if (!el) return;

    el.value = formatCurrencyValue(el.value);

    el.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/[^0-9,\.]/g, '');
    });

    el.addEventListener('blur', function(e) {
        e.target.value = formatCurrencyValue(e.target.value);
    });

    el.addEventListener('input', calcularTotal);
}

/**
 * Formata valor para moeda brasileira
 */
function formatCurrencyValue(value) {
    if (value === null || value === undefined) return '0,00';
    const cleaned = String(value).replace(/[^0-9,\.]/g, '');
    if (cleaned === '') return '0,00';
    const normalized = cleaned.replace(/\.(?=.*\.)/g, '').replace(/,/g, '.');
    const num = parseFloat(normalized);
    if (isNaN(num)) return '0,00';
    return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num);
}

/**
 * Converte string de moeda para float
 */
function parseCurrencyToFloat(str) {
    if (!str) return 0;
    const cleaned    = String(str).replace(/[^0-9,\.]/g, '').trim();
    if (cleaned === '') return 0;
    const normalized = cleaned.replace(/\r/g, '');
    const n          = parseFloat(normalized);
    return isNaN(n) ? 0 : n;
}

/**
 * Inicializa contador de observação
 */
function inicializarContadorObservacao() {
    const obsElem    = document.getElementById('observacao');
    const obsCounter = document.getElementById('obs-counter');

    if (obsElem && obsCounter) {
        obsElem.addEventListener('input', function() {
            obsCounter.textContent = this.value.length;
        });
    }
}

/**
 * Envia dados do orçamento para o servidor
 */
async function finalizarOrcamento(e) {
    e.preventDefault();

    const clienteId        = document.getElementById('cliente').value;
    const formaPagamentoId = document.getElementById('forma-pagamento').value;

    if (!clienteId) {
        alert('Selecione um cliente');
        return;
    }
    if (itensOrcamento.length === 0) {
        alert('Adicione pelo menos um produto');
        return;
    }
    if (!formaPagamentoId) {
        alert('Selecione uma forma de pagamento');
        return;
    }

    const totalOrcamento = itensOrcamento.reduce((sum, item) => sum + item.valor_total, 0);
    if (!confirm(`Confirmar orçamento no valor de R$ ${totalOrcamento.toFixed(2)}?`)) {
        return;
    }

    let parcelamento = '';
    const parcelamentoGrupo = document.getElementById('parcelamento-grupo');
    if (parcelamentoGrupo && parcelamentoGrupo.style.display !== 'none') {
        const parcelamentoSelect = document.getElementById('parcelamento');
        if (parcelamentoSelect) {
            parcelamento = parcelamentoSelect.value;
        }
    }

    const dados = {
        cliente_id:        parseInt(clienteId),
        forma_pagamento_id: parseInt(formaPagamentoId),
        desconto:   parseCurrencyToFloat(document.getElementById('desconto').value) || 0,
        frete:      parseCurrencyToFloat(document.getElementById('frete').value) || 0,
        parcelamento,
        itens:      itensOrcamento,
        observacao: document.getElementById('observacao')?.value.trim() || ''
    };

    try {
        const response = await fetch(window.urls.criarOrcamento, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(dados)
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);

            if (result.orcamento_id) {
                const link = document.createElement('a');
                link.href = `/orcamentos/pdf/${result.orcamento_id}/`;
                link.download = `orcamento_${result.orcamento_id}.pdf`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

            setTimeout(() => {
                window.location.href = window.urls.orcamentos;
            }, 1500);
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao finalizar orçamento:', error);
        alert('Erro ao finalizar. Verifique o console.');
    }
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
window.novoOrcamento = {
    adicionarItem,
    removerItem,
    calcularTotal,
    finalizarOrcamento,
    getCookie
};