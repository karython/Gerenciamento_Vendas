/**
 * Nova Venda JavaScript
 * Lógica para criação de novas vendas
 */

// Variáveis globais
let itensVenda = [];
let produtosDisponiveis = [];

/**
 * Inicialização quando o DOM está pronto
 */
document.addEventListener("DOMContentLoaded", function() {
    carregarClientes();
    carregarProdutos();
    carregarFormasPagamento();
    inicializarMascarasMoeda();
    inicializarContadorObservacao();
    inicializarEventListeners();
});

/**
 * Inicializa event listeners para botões e formulários
 */
function inicializarEventListeners() {
    // Botão adicionar item
    const btnAdicionar = document.getElementById('btn-adicionar');
    if (btnAdicionar) {
        btnAdicionar.addEventListener('click', adicionarItem);
    }
    
    // Formulário de venda
    const formVenda = document.getElementById('form-nova-venda');
    if (formVenda) {
        formVenda.addEventListener('submit', finalizarVenda);
    }
}

/**
 * Carrega lista de clientes do banco
 */
async function carregarClientes() {
    try {
        console.log('Carregando clientes...');
        const response = await fetch(window.urls.clientes);
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
 * Carrega lista de produtos do estoque
 */
async function carregarProdutos() {
    try {
        console.log('Carregando produtos...');
        const response = await fetch(window.urls.produtos);
        const data = await response.json();
        
        if (data.success) {
            produtosDisponiveis = data.produtos;
            const select = document.getElementById('produto');
            select.innerHTML = '<option value="">Buscar por ID ou Nome do Produto...</option>';
            
            data.produtos.forEach(produto => {
                const option = document.createElement('option');
                option.value = produto.id;
                option.textContent = produto.label;
                option.dataset.valor = produto.valor;
                option.dataset.estoque = produto.estoque;
                option.dataset.descricao = produto.descricao;
                option.dataset.isService = produto.is_service;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
    }
}

/**
 * Carrega formas de pagamento
 */
async function carregarFormasPagamento() {
    try {
        console.log('Carregando formas de pagamento...');
        const response = await fetch(window.urls.formasPagamento);
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
            
            // Adicionar event listener para mostrar/ocultar parcelamento
            select.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                const tipoForma = selectedOption.dataset.tipo;
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
 * Adiciona item à venda
 */
function adicionarItem() {
    const produtoSelect = document.getElementById('produto');
    const quantidadeInput = document.getElementById('quantidade');
    
    const produtoId = produtoSelect.value;
    const quantidade = parseInt(quantidadeInput.value);
    
    if (!produtoId) {
        alert('Selecione um produto do estoque');
        return;
    }
    
    if (!quantidade || quantidade < 1) {
        alert('Informe uma quantidade válida');
        return;
    }
    
    const option = produtoSelect.options[produtoSelect.selectedIndex];
    const estoque = parseInt(option.dataset.estoque);
    const isService = option.dataset.isService === 'true';

    if (!isService && quantidade > estoque) {
        alert(`Estoque insuficiente! Disponível: ${estoque} unidades`);
        return;
    }
    
    // Verificar se produto já está na lista
    const itemExistente = itensVenda.find(item => item.produto_id === parseInt(produtoId));
    if (itemExistente) {
        alert('Produto já adicionado! Remova-o primeiro para alterar a quantidade.');
        return;
    }
    
    let valorUnitario = parseFloat(option.dataset.valor);

    // Se for serviço, permitir inserir/editar o valor unitário livremente
    if (isService) {
        const input = prompt('Produto serviço: informe o valor unitário (use vírgula ou ponto):', option.dataset.valor);
        if (input === null) return; // usuario cancelou
        // Normalizar entrada (trocar vírgula por ponto)
        const normalized = String(input).replace(/\s+/g, '').replace(/,/g, '.');
        valorUnitario = parseFloat(normalized);
        if (isNaN(valorUnitario) || valorUnitario <= 0) {
            alert('Valor inválido para o serviço');
            return;
        }
    }

    const valorTotal = quantidade * valorUnitario;
    
    const item = {
        produto_id: parseInt(produtoId),
        descricao: option.dataset.descricao,
        quantidade: quantidade,
        valor_unitario: valorUnitario,
        valor_total: valorTotal
    };
    
    itensVenda.push(item);
    atualizarTabelaItens();
    
    // Limpar campos
    produtoSelect.value = '';
    quantidadeInput.value = 1;
}

/**
 * Atualiza tabela de itens da venda
 */
function atualizarTabelaItens() {
    const tbody = document.getElementById('itens-venda');
    
    if (itensVenda.length === 0) {
        tbody.innerHTML = '<tr id="linha-vazia"><td colspan="5" style="text-align: center;">Nenhum item adicionado</td></tr>';
        document.getElementById('subtotal').textContent = 'R$ 0,00';
        document.getElementById('total').textContent = 'R$ 0,00';
        return;
    }
    
    tbody.innerHTML = '';
    let subtotal = 0;
    
    itensVenda.forEach((item, index) => {
        subtotal += item.valor_total;
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.descricao}</td>
            <td style="text-align: center;">${item.quantidade}</td>
            <td>R$ ${item.valor_unitario.toFixed(2)}</td>
            <td>R$ ${item.valor_total.toFixed(2)}</td>
            <td style="text-align: center;">
                <button type="button" class="btn-remover" data-index="${index}"
                        title="Remover item">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
    
    // Adicionar event listeners para botões de remover
    tbody.querySelectorAll('.btn-remover').forEach(btn => {
        btn.addEventListener('click', function() {
            const index = parseInt(this.dataset.index);
            removerItem(index);
        });
    });
    
    document.getElementById('subtotal').textContent = `R$ ${subtotal.toFixed(2)}`;
    calcularTotal();
}

/**
 * Remove item da venda
 */
function removerItem(index) {
    if (confirm('Deseja remover este item?')) {
        itensVenda.splice(index, 1);
        atualizarTabelaItens();
    }
}

/**
 * Calcula total com desconto e frete
 */
function calcularTotal() {
    const subtotal = itensVenda.reduce((sum, item) => sum + item.valor_total, 0);
    const desconto = parseCurrencyToFloat(document.getElementById('desconto').value) || 0;
    const frete = parseCurrencyToFloat(document.getElementById('frete').value) || 0;
    const total = subtotal - desconto + frete;

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
    
    // Formatar ao carregar
    el.value = formatCurrencyValue(el.value);
    
    // Limpa caracteres inválidos durante digitação
    el.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/[^0-9,\.]/g,'');
    });
    
    // Formata ao sair do campo
    el.addEventListener('blur', function(e) {
        e.target.value = formatCurrencyValue(e.target.value);
    });
    
    // Atualizar total quando campo mudar
    el.addEventListener('input', calcularTotal);
}

/**
 * Formata valor para moeda brasileira
 */
function formatCurrencyValue(value) {
    if (value === null || value === undefined) return '0,00';
    const cleaned = String(value).replace(/[^0-9,\.]/g,'');
    if (cleaned === '') return '0,00';
    const normalized = cleaned.replace(/\.(?=.*\.)/g,'').replace(/,/g,'.');
    const num = parseFloat(normalized);
    if (isNaN(num)) return '0,00';
    return new Intl.NumberFormat('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(num);
}

/**
 * Converte string de moeda para float
 */
function parseCurrencyToFloat(str) {
    if (!str) return 0;
    const cleaned = String(str).replace(/[^0-9,\.]/g,'').trim();
    if (cleaned === '') return 0;
    const normalized = cleaned.replace(/\r/g,'');
    const n = parseFloat(normalized);
    return isNaN(n) ? 0 : n;
}

/**
 * Inicializa contador de observação
 */
function inicializarContadorObservacao() {
    const obsElem = document.getElementById('observacao');
    const obsCounter = document.getElementById('obs-counter');
    
    if (obsElem && obsCounter) {
        obsElem.addEventListener('input', function() {
            obsCounter.textContent = this.value.length;
        });
    }
}

/**
 * Envia dados da venda para o servidor
 */
async function finalizarVenda(e) {
    e.preventDefault();
    
    const clienteId = document.getElementById('cliente').value;
    const formaPagamentoId = document.getElementById('forma-pagamento').value;
    const desconto = parseCurrencyToFloat(document.getElementById('desconto').value) || 0;
    const frete = parseCurrencyToFloat(document.getElementById('frete').value) || 0;

    if (!clienteId) {
        alert('Selecione um cliente');
        return;
    }
    if (itensVenda.length === 0) {
        alert('Adicione pelo menos um produto');
        return;
    }
    if (!formaPagamentoId) {
        alert('Selecione uma forma de pagamento');
        return;
    }
    
    const totalVenda = itensVenda.reduce((sum, item) => sum + item.valor_total, 0) - desconto + frete;
    if (!confirm(`Confirmar venda no valor de R$ ${totalVenda.toFixed(2)}?`)) {
        return;
    }
    
    // Pegar parcelamento se existir e estiver visível
    let parcelamento = '';
    const parcelamentoGrupo = document.getElementById('parcelamento-grupo');
    if (parcelamentoGrupo && parcelamentoGrupo.style.display !== 'none') {
        const parcelamentoSelect = document.getElementById('parcelamento');
        if (parcelamentoSelect) {
            parcelamento = parcelamentoSelect.value;
        }
    }
    
    const dados = {
        cliente_id: parseInt(clienteId),
        forma_pagamento_id: parseInt(formaPagamentoId),
        desconto: desconto,
        frete: frete,
        parcelamento: parcelamento,
        itens: itensVenda,
        observacao: document.getElementById('observacao')?.value.trim() || ''
    };
    
    try {
        const response = await fetch(window.urls.criarVenda, {
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
            window.open(`/vendas/pdf/${result.venda_id}/`, '_blank');
            setTimeout(() => { window.location.href = window.urls.vendas; }, 1000);
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro ao finalizar venda:', error);
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

// Expor funções globalmente para uso nos templates
window.novaVenda = {
    adicionarItem,
    removerItem,
    calcularTotal,
    finalizarVenda,
    getCookie
};

