/**
 * Dashboard Charts — dinâmico com filtros e Chart.js 4
 */

// ── Paleta de cores ──────────────────────────────────────────────────────────
const CORES = [
    '#27ae60', '#2980b9', '#e67e22', '#8e44ad',
    '#e74c3c', '#16a085', '#d35400', '#f39c12',
];

const BRL = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

// ── Estado ───────────────────────────────────────────────────────────────────
let chartVendasDia   = null;
let chartTopProdutos = null;
let chartFormas      = null;
let metricaAtiva     = 'qtd';
let filtros          = { periodo: '90', data_inicio: '', data_fim: '', produto_id: '' };

// ── Bootstrap ────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    configurarFiltros();
    carregarDados();
});

// ── Configuração de filtros ──────────────────────────────────────────────────
function configurarFiltros() {
    document.querySelectorAll('.btn-periodo').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-periodo').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const periodo   = btn.dataset.periodo;
            const divDatas  = document.getElementById('filtro-datas');

            if (periodo === 'personalizado') {
                divDatas.style.display = 'flex';
            } else {
                divDatas.style.display = 'none';
                filtros.periodo     = periodo;
                filtros.data_inicio = '';
                filtros.data_fim    = '';
                carregarDados();
            }
        });
    });

    document.getElementById('btn-aplicar-datas').addEventListener('click', () => {
        const di = document.getElementById('data-inicio').value;
        const df = document.getElementById('data-fim').value;
        if (!di || !df)  { alert('Informe data inicial e final'); return; }
        if (di > df)     { alert('Data inicial deve ser anterior à final'); return; }
        filtros.periodo     = '';
        filtros.data_inicio = di;
        filtros.data_fim    = df;
        carregarDados();
    });

    document.getElementById('filtro-produto').addEventListener('change', function () {
        filtros.produto_id = this.value;
        carregarDados();
    });

    document.querySelectorAll('.btn-chart-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-chart-toggle').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            metricaAtiva = btn.dataset.metric;
            if (window._ultimoDado) renderizarGraficoLinha(window._ultimoDado.vendas_dia);
        });
    });
}

// ── Busca de dados ───────────────────────────────────────────────────────────
async function carregarDados() {
    mostrarLoading(true);

    const params = new URLSearchParams();
    if (filtros.periodo)     params.set('periodo',     filtros.periodo);
    if (filtros.data_inicio) params.set('data_inicio', filtros.data_inicio);
    if (filtros.data_fim)    params.set('data_fim',    filtros.data_fim);
    if (filtros.produto_id)  params.set('produto_id',  filtros.produto_id);

    try {
        const res  = await fetch(`${window.dashboardUrls.api}?${params}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        window._ultimoDado = data;
        renderizarDashboard(data);
    } catch (err) {
        console.error('Erro ao carregar dashboard:', err);
    } finally {
        mostrarLoading(false);
    }
}

// ── Renderização ─────────────────────────────────────────────────────────────
function renderizarDashboard(data) {
    atualizarKPIs(data.kpis);
    atualizarPeriodoLabel(data.periodo);
    renderizarGraficoLinha(data.vendas_dia);
    renderizarGraficoTopProdutos(data.top_produtos);
    renderizarGraficoFormas(data.formas_pagamento);

    document.getElementById('dash-vazio').style.display =
        data.kpis.total_vendas === 0 ? 'flex' : 'none';
}

function atualizarKPIs(kpis) {
    set('kpi-receita-bruta',   BRL.format(kpis.receita_bruta));
    set('kpi-receita-liquida', BRL.format(kpis.receita_liquida));
    set('kpi-total-vendas',    kpis.total_vendas);
    set('kpi-ticket-medio',    BRL.format(kpis.ticket_medio));
}

function atualizarPeriodoLabel(periodo) {
    const el = document.getElementById('periodo-label');
    if (el) el.textContent = `${periodo.inicio} — ${periodo.fim}`;
}

// ── Helpers de chart — destrói antes de recriar para evitar estado stale ─────
function destruir(instancia) {
    try { if (instancia) instancia.destroy(); } catch (_) {}
    return null;
}

function canvasCtx(id) {
    const el = document.getElementById(id);
    return el ? el.getContext('2d') : null;
}

// ── Gráfico de linha: Vendas por dia ─────────────────────────────────────────
function renderizarGraficoLinha(vendas_dia) {
    chartVendasDia = destruir(chartVendasDia);

    const ctx = canvasCtx('graficoVendasDia');
    if (!ctx) return;

    const labels  = vendas_dia.labels  || [];
    const valores = metricaAtiva === 'qtd' ? (vendas_dia.qtd || []) : (vendas_dia.receita || []);

    if (labels.length === 0) {
        mostrarMensagemVazio('wrap-vendas-dia', 'Sem vendas no período selecionado');
        return;
    }

    esconderMensagemVazio('wrap-vendas-dia');

    chartVendasDia = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label:                metricaAtiva === 'qtd' ? 'Vendas' : 'Receita (R$)',
                data:                 valores,
                borderColor:          '#27ae60',
                backgroundColor:      'rgba(39, 174, 96, 0.12)',
                borderWidth:          2.5,
                tension:              0.4,
                fill:                 true,
                pointBackgroundColor: '#fff',
                pointBorderColor:     '#27ae60',
                pointBorderWidth:     2,
                pointRadius:          labels.length > 60 ? 0 : 4,
                pointHoverRadius:     6,
            }],
        },
        options: {
            responsive:          true,
            maintainAspectRatio: false,
            interaction:         { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(30,30,30,0.85)',
                    padding: 12,
                    callbacks: {
                        label: (c) => metricaAtiva === 'qtd'
                            ? ` ${c.parsed.y} venda(s)`
                            : ` ${BRL.format(c.parsed.y)}`,
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#f0f0f0' },
                    ticks: {
                        padding: 8,
                        callback: (v) => metricaAtiva === 'receita' ? BRL.format(v) : v,
                    },
                },
                x: {
                    grid: { display: false },
                    ticks: { padding: 8, maxTicksLimit: 14 },
                },
            },
        },
    });
}

// ── Gráfico de barras horizontais: Top Produtos ───────────────────────────────
function renderizarGraficoTopProdutos(top) {
    chartTopProdutos = destruir(chartTopProdutos);

    const ctx = canvasCtx('graficoTopProdutos');
    if (!ctx) return;

    const labels = (top.labels || []).map(l => l.length > 28 ? l.slice(0, 26) + '…' : l);

    if (labels.length === 0) {
        mostrarMensagemVazio('wrap-top-produtos', 'Sem produtos no período');
        return;
    }

    esconderMensagemVazio('wrap-top-produtos');

    chartTopProdutos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label:           'Receita (R$)',
                data:            top.receita || [],
                backgroundColor: CORES.slice(0, labels.length),
                borderRadius:    6,
                borderSkipped:   false,
            }],
        },
        options: {
            indexAxis:           'y',
            responsive:          true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: { label: (c) => ` ${BRL.format(c.parsed.x)}` },
                },
            },
            scales: {
                x: {
                    grid:  { color: '#f0f0f0' },
                    ticks: { callback: (v) => BRL.format(v) },
                },
                y: { grid: { display: false } },
            },
        },
    });
}

// ── Gráfico doughnut: Formas de pagamento ─────────────────────────────────────
function renderizarGraficoFormas(formas) {
    chartFormas = destruir(chartFormas);

    const ctx = canvasCtx('graficoFormas');
    if (!ctx) return;

    const labels = formas.labels || [];

    if (labels.length === 0) {
        mostrarMensagemVazio('wrap-formas', 'Sem dados no período');
        return;
    }

    esconderMensagemVazio('wrap-formas');

    chartFormas = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data:            formas.receita || [],
                backgroundColor: CORES,
                borderWidth:     0,
                hoverOffset:     6,
            }],
        },
        options: {
            responsive:          true,
            maintainAspectRatio: false,
            cutout:              '68%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels:   { boxWidth: 12, padding: 14, usePointStyle: true },
                },
                tooltip: {
                    callbacks: { label: (c) => ` ${c.label}: ${BRL.format(c.parsed)}` },
                },
            },
        },
    });
}

// ── Estado vazio por gráfico ──────────────────────────────────────────────────
function mostrarMensagemVazio(wrapId, msg) {
    const wrap = document.getElementById(wrapId);
    if (!wrap) return;
    let el = wrap.querySelector('.grafico-vazio');
    if (!el) {
        el = document.createElement('div');
        el.className = 'grafico-vazio';
        wrap.appendChild(el);
    }
    el.textContent = msg;
    el.style.display = 'flex';
    const canvas = wrap.querySelector('canvas');
    if (canvas) canvas.style.display = 'none';
}

function esconderMensagemVazio(wrapId) {
    const wrap = document.getElementById(wrapId);
    if (!wrap) return;
    const el = wrap.querySelector('.grafico-vazio');
    if (el) el.style.display = 'none';
    const canvas = wrap.querySelector('canvas');
    if (canvas) canvas.style.display = 'block';
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function mostrarLoading(ativo) {
    document.querySelectorAll('.chart-loading').forEach(el => {
        el.style.display = ativo ? 'flex' : 'none';
    });
}

function set(id, valor) {
    const el = document.getElementById(id);
    if (el) el.textContent = valor;
}
