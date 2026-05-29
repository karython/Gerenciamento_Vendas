/**
 * Editar Orçamento — pré-carrega os dados existentes e permite modificações.
 */

let itensOrcamento = [];
let produtosDisponiveis = [];

document.addEventListener('DOMContentLoaded', function () {
    inicializarEventListeners();

    // Itens não dependem de fetch — preencher imediatamente
    preencherItensIniciais();

    // Dados async em paralelo
    carregarClientes();
    carregarProdutos();
    carregarFormasPagamento();

    inicializarMascarasMoeda();
    inicializarContadorObservacao();
});

function inicializarEventListeners() {
    document.getElementById('btn-adicionar').addEventListener('click', adicionarItem);
    document.getElementById('form-editar-orcamento').addEventListener('submit', salvarEdicao);
}

// ---------------------------------------------------------------------------
// Pré-preenchimento dos dados do orçamento
// ---------------------------------------------------------------------------

function preencherItensIniciais() {
    const edicao = window.orcamentoEdicao;

    edicao.itensIniciais.forEach(item => {
        itensOrcamento.push({
            produto_id:     item.produto_id,
            descricao:      item.descricao,
            quantidade:     item.quantidade,
            valor_unitario: item.valor_unitario,
            valor_total:    item.valor_total,
        });
    });

    // Preencher desconto e frete (valores vêm do JSON — sempre com ponto decimal)
    document.getElementById('desconto').value = formatCurrencyValue(String(edicao.desconto));
    document.getElementById('frete').value    = formatCurrencyValue(String(edicao.frete));

    atualizarTabelaItens();
    calcularTotal();
}

// ---------------------------------------------------------------------------
// Carregamento de dados via API
// ---------------------------------------------------------------------------

async function carregarClientes() {
    const select       = document.getElementById('cliente');
    const clienteAtual = parseInt(select.dataset.currentId);
    try {
        const response = await fetch(window.urls.buscarClientes);
        const data     = await response.json();

        if (data.success) {
            const valorAtual = parseInt(select.value);
            select.innerHTML = '';
            data.clientes.forEach(cliente => {
                const opt       = document.createElement('option');
                opt.value       = cliente.id;
                opt.textContent = cliente.label;
                // Manter a seleção atual do usuário (pode já ter mudado)
                opt.selected    = cliente.id === (valorAtual || clienteAtual);
                select.appendChild(opt);
            });
        }
    } catch (err) {
        console.error('Erro ao carregar clientes:', err);
        // Mantém o option pré-populado do template — sem perda
    }
}

async function carregarProdutos() {
    try {
        const response = await fetch(window.urls.buscarProdutos);
        const data     = await response.json();

        if (data.success) {
            produtosDisponiveis = data.produtos;
            inicializarAutocompleteProduto();
        }
    } catch (err) {
        console.error('Erro ao carregar produtos:', err);
    }
}

async function carregarFormasPagamento() {
    const select          = document.getElementById('forma-pagamento');
    const fpAtual         = parseInt(select.dataset.currentId);
    const parcelAtual     = select.dataset.currentParcelamento || '';

    // Listener de parcelamento — registrar uma vez
    select.addEventListener('change', function () {
        const tipo  = this.options[this.selectedIndex]?.dataset.tipo || '';
        const grupo = document.getElementById('parcelamento-grupo');
        grupo.style.display =
            tipo.includes('cartão de crédito') || tipo.includes('crédito')
                ? 'block' : 'none';
    });

    try {
        const response = await fetch(window.urls.buscarFormasPagamento);
        const data     = await response.json();

        if (data.success) {
            const valorAtual = parseInt(select.value);
            select.innerHTML = '';

            data.formas_pagamento.forEach(forma => {
                const opt        = document.createElement('option');
                opt.value        = forma.id;
                opt.textContent  = forma.tipo;
                opt.dataset.tipo = forma.tipo.toLowerCase();
                opt.selected     = forma.id === (valorAtual || fpAtual);
                select.appendChild(opt);
            });

            select.dispatchEvent(new Event('change'));

            // Pré-selecionar parcelamento
            if (parcelAtual) {
                const parcelaSelect = document.getElementById('parcelamento');
                for (const opt of parcelaSelect.options) {
                    if (opt.value === parcelAtual) { opt.selected = true; break; }
                }
            }
        }
    } catch (err) {
        console.error('Erro ao carregar formas de pagamento:', err);
        // Mantém o option pré-populado do template
    }
}

// ---------------------------------------------------------------------------
// Autocomplete de produto
// ---------------------------------------------------------------------------

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
        if (lista.length === 0) { dropdown.style.display = 'none'; return; }

        lista.forEach((produto, idx) => {
            const li = document.createElement('li');
            li.textContent = produto.label;
            li.style.cssText = 'padding:10px 14px;cursor:pointer;border-bottom:1px solid #f0f0f0;font-size:.95em;';
            li.addEventListener('mouseenter', () => { removeHighlights(); highlightIdx = idx; li.style.background = '#f0f4ff'; });
            li.addEventListener('mouseleave', () => { li.style.background = ''; });
            li.addEventListener('mousedown', e => { e.preventDefault(); selecionarProduto(produto); });
            dropdown.appendChild(li);
        });
        dropdown.style.display = 'block';
    }

    function removeHighlights() {
        dropdown.querySelectorAll('li').forEach(li => li.style.background = '');
    }

    function selecionarProduto(produto) {
        hidden.value             = produto.id;
        hidden.dataset.valor     = produto.valor;
        hidden.dataset.estoque   = produto.estoque;
        hidden.dataset.descricao = produto.descricao;
        hidden.dataset.isService = produto.is_service;
        input.value              = produto.label;
        dropdown.style.display   = 'none';
        document.getElementById('quantidade').focus();
    }

    function filtrar(texto) {
        if (!texto.trim()) { renderDropdown([]); return; }
        const termo = texto.toLowerCase();
        renderDropdown(produtosDisponiveis.filter(p =>
            p.label.toLowerCase().includes(termo) || String(p.id).includes(termo)
        ));
    }

    input.addEventListener('input', () => { hidden.value = ''; filtrar(input.value); });
    input.addEventListener('focus', () => { if (input.value.trim()) filtrar(input.value); });
    document.addEventListener('click', e => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) dropdown.style.display = 'none';
    });
    input.addEventListener('keydown', e => {
        const items = dropdown.querySelectorAll('li');
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            highlightIdx = Math.min(highlightIdx + 1, items.length - 1);
            removeHighlights();
            if (items[highlightIdx]) items[highlightIdx].style.background = '#f0f4ff';
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightIdx = Math.max(highlightIdx - 1, 0);
            removeHighlights();
            if (items[highlightIdx]) items[highlightIdx].style.background = '#f0f4ff';
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlightIdx >= 0 && filtradosAtual[highlightIdx]) selecionarProduto(filtradosAtual[highlightIdx]);
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none';
        }
    });
}

// ---------------------------------------------------------------------------
// Itens
// ---------------------------------------------------------------------------

function adicionarItem() {
    const hidden          = document.getElementById('produto');
    const inputTexto      = document.getElementById('produto-input');
    const quantidadeInput = document.getElementById('quantidade');

    const produtoId  = hidden.value;
    const quantidade = parseInt(quantidadeInput.value);

    if (!produtoId)                    { alert('Selecione um produto da lista'); return; }
    if (!quantidade || quantidade < 1) { alert('Informe uma quantidade válida'); return; }

    const estoque   = parseInt(hidden.dataset.estoque);
    const isService = hidden.dataset.isService === 'true';

    if (!isService && quantidade > estoque) {
        const ok = confirm(
            `Atenção: estoque disponível é ${estoque} unidade(s).\n` +
            `Orçamentos não dão baixa no estoque — deseja adicionar mesmo assim?`
        );
        if (!ok) return;
    }

    if (itensOrcamento.find(i => i.produto_id === parseInt(produtoId))) {
        alert('Produto já adicionado! Remova-o primeiro para alterar a quantidade.');
        return;
    }

    let valorUnitario = parseFloat(hidden.dataset.valor);

    if (isService) {
        const inp = prompt('Produto serviço: informe o valor unitário:', hidden.dataset.valor);
        if (inp === null) return;
        valorUnitario = parseFloat(String(inp).replace(/\s+/g, '').replace(/,/g, '.'));
        if (isNaN(valorUnitario) || valorUnitario <= 0) { alert('Valor inválido para o serviço'); return; }
    }

    itensOrcamento.push({
        produto_id:     parseInt(produtoId),
        descricao:      hidden.dataset.descricao,
        quantidade:     quantidade,
        valor_unitario: valorUnitario,
        valor_total:    quantidade * valorUnitario,
    });

    atualizarTabelaItens();
    hidden.value = ''; inputTexto.value = ''; quantidadeInput.value = 1;
    inputTexto.focus();
}

function removerItem(index) {
    itensOrcamento.splice(index, 1);
    atualizarTabelaItens();
}

function atualizarTabelaItens() {
    const tbody = document.getElementById('itens-orcamento');

    if (itensOrcamento.length === 0) {
        tbody.innerHTML = '<tr id="linha-vazia"><td colspan="5" style="text-align:center;padding:20px;color:#777;">Nenhum item adicionado</td></tr>';
        document.getElementById('subtotal').textContent = 'R$ 0,00';
        document.getElementById('total').textContent    = 'R$ 0,00';
        return;
    }

    tbody.innerHTML = '';
    let subtotal = 0;

    itensOrcamento.forEach((item, index) => {
        subtotal += item.valor_total;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.descricao}</td>
            <td style="text-align:center;">${item.quantidade}</td>
            <td>R$ ${parseFloat(item.valor_unitario).toFixed(2)}</td>
            <td>R$ ${parseFloat(item.valor_total).toFixed(2)}</td>
            <td style="text-align:center;">
                <button type="button" class="btn-acao btn-deletar btn-remover" data-index="${index}" title="Remover">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>`;
        tbody.appendChild(tr);
    });

    tbody.querySelectorAll('.btn-remover').forEach(btn => {
        btn.addEventListener('click', function () { removerItem(parseInt(this.dataset.index)); });
    });

    document.getElementById('subtotal').textContent = `R$ ${subtotal.toFixed(2)}`;
    calcularTotal();
}

// ---------------------------------------------------------------------------
// Cálculos e máscaras
// ---------------------------------------------------------------------------

function calcularTotal() {
    const subtotal = itensOrcamento.reduce((s, i) => s + parseFloat(i.valor_total), 0);
    const desconto = parseCurrencyToFloat(document.getElementById('desconto').value) || 0;
    const frete    = parseCurrencyToFloat(document.getElementById('frete').value) || 0;
    document.getElementById('total').textContent = `R$ ${(subtotal - desconto + frete).toFixed(2)}`;
}

function inicializarMascarasMoeda() {
    attachCurrencyMask('desconto');
    attachCurrencyMask('frete');
}

function attachCurrencyMask(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('input', function (e) { e.target.value = e.target.value.replace(/[^0-9,\.]/g, ''); });
    el.addEventListener('blur',  function (e) { e.target.value = formatCurrencyValue(e.target.value); });
    el.addEventListener('input', calcularTotal);
}

function formatCurrencyValue(value) {
    if (!value && value !== 0) return '0,00';
    const cleaned    = String(value).replace(/[^0-9,\.]/g, '');
    if (!cleaned)    return '0,00';
    const normalized = cleaned.replace(/\.(?=.*\.)/g, '').replace(/,/g, '.');
    const num        = parseFloat(normalized);
    if (isNaN(num))  return '0,00';
    return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(num);
}

function parseCurrencyToFloat(str) {
    if (!str && str !== 0) return 0;
    const cleaned = String(str).replace(/[^0-9,\.]/g, '').trim();
    if (!cleaned) return 0;

    let normalized;
    if (cleaned.includes(',') && cleaned.includes('.')) {
        // Formato BR com milhar: "1.234,56" → "1234.56"
        normalized = cleaned.replace(/\./g, '').replace(',', '.');
    } else if (cleaned.includes(',')) {
        // Formato BR sem milhar: "10,50" → "10.50"
        normalized = cleaned.replace(',', '.');
    } else {
        normalized = cleaned;
    }

    const n = parseFloat(normalized);
    return isNaN(n) ? 0 : n;
}

function inicializarContadorObservacao() {
    const obs     = document.getElementById('observacao');
    const counter = document.getElementById('obs-counter');
    if (obs && counter) {
        obs.addEventListener('input', function () { counter.textContent = this.value.length; });
    }
}

// ---------------------------------------------------------------------------
// Submissão
// ---------------------------------------------------------------------------

async function salvarEdicao(e) {
    e.preventDefault();

    const clienteId        = document.getElementById('cliente').value;
    const formaPagamentoId = document.getElementById('forma-pagamento').value;

    if (!clienteId)                    { alert('Selecione um cliente'); return; }
    if (itensOrcamento.length === 0)   { alert('Adicione pelo menos um produto'); return; }
    if (!formaPagamentoId)             { alert('Selecione uma forma de pagamento'); return; }

    const totalOrcamento = itensOrcamento.reduce((s, i) => s + parseFloat(i.valor_total), 0);
    const idFormatado    = String(window.orcamentoEdicao.id).padStart(5, '0');

    if (!confirm(`Salvar alterações no orçamento OR-${idFormatado}?\nTotal: R$ ${totalOrcamento.toFixed(2)}`)) return;

    let parcelamento = '';
    const parcelamentoGrupo = document.getElementById('parcelamento-grupo');
    if (parcelamentoGrupo && parcelamentoGrupo.style.display !== 'none') {
        parcelamento = document.getElementById('parcelamento').value;
    }

    const dados = {
        cliente_id:         parseInt(clienteId),
        forma_pagamento_id: parseInt(formaPagamentoId),
        desconto:    parseCurrencyToFloat(document.getElementById('desconto').value) || 0,
        frete:       parseCurrencyToFloat(document.getElementById('frete').value) || 0,
        parcelamento,
        itens:       itensOrcamento,
        observacao:  document.getElementById('observacao')?.value.trim() || '',
    };

    try {
        const response = await fetch(window.urls.salvarEdicao, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(dados),
        });

        const result = await response.json();

        if (result.success) {
            alert(result.message);
            window.location.href = window.urls.orcamentos;
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (err) {
        console.error('Erro ao salvar:', err);
        alert('Erro ao salvar. Verifique o console.');
    }
}

function getCookie(name) {
    let value = null;
    if (document.cookie) {
        for (const cookie of document.cookie.split(';')) {
            const c = cookie.trim();
            if (c.startsWith(name + '=')) {
                value = decodeURIComponent(c.slice(name.length + 1));
                break;
            }
        }
    }
    return value;
}
