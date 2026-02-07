/**
 * Dashboard Charts JavaScript
 * Configuração dos gráficos do dashboard usando Chart.js
 */

document.addEventListener("DOMContentLoaded", function() {
    initVendasChart();
    initReceitaChart();
});

/**
 * Gráfico de Vendas por Dia (Linha com Degradê)
 */
function initVendasChart() {
    const ctxVendas = document.getElementById('graficoVendas');
    
    if (!ctxVendas) {
        console.warn('Canvas graficoVendas não encontrado');
        return;
    }

    const chartCtx = ctxVendas.getContext('2d');
    
    // Parsear dados do backend - os dados já vêm como JSON processado pelo Django
    let datasVendasRaw = [];
    let valoresVendasRaw = [];
    
    try {
        const datasElement = document.getElementById('datas-vendas-data');
        const valoresElement = document.getElementById('valores-vendas-data');
        
        if (datasElement && valoresElement) {
            datasVendasRaw = JSON.parse(datasElement.textContent);
            valoresVendasRaw = JSON.parse(valoresElement.textContent);
        }
    } catch (e) {
        console.warn('Erro ao parsear dados dos gráficos:', e);
    }
    
    if (!datasVendasRaw || datasVendasRaw.length === 0) {
        console.warn('Nenhum dado de vendas disponível');
        return;
    }

    // Criar degradê
    let gradientVendas = chartCtx.createLinearGradient(0, 0, 0, 400);
    gradientVendas.addColorStop(0, 'rgba(46, 204, 113, 0.5)');
    gradientVendas.addColorStop(1, 'rgba(46, 204, 113, 0.0)');

    // Configuração comum
    Chart.defaults.font.family = "'Segoe UI', 'Helvetica Neue', 'Arial', sans-serif";
    Chart.defaults.color = '#666';

    new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: datasVendasRaw,
            datasets: [{
                label: 'Vendas',
                data: valoresVendasRaw,
                borderColor: '#27ae60',
                backgroundColor: gradientVendas,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#27ae60',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (c) => c.parsed.y + ' Vendas'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { borderDash: [5, 5], color: '#f0f0f0' },
                    ticks: { padding: 10 }
                },
                x: {
                    grid: { display: false },
                    ticks: { padding: 10 }
                }
            }
        }
    });
}

/**
 * Gráfico de Receita (Doughnut)
 */
function initReceitaChart() {
    const ctxReceita = document.getElementById('graficoReceita');
    
    if (!ctxReceita) {
        console.warn('Canvas graficoReceita não encontrado');
        return;
    }

    // Parsear dados do backend
    let receitaBrutaRaw = 0;
    let receitaLiquidaRaw = 0;
    
    try {
        const receitaBrutaElement = document.getElementById('receita-bruta');
        const receitaLiquidaElement = document.getElementById('receita-liquida');
        
        if (receitaBrutaElement && receitaLiquidaElement) {
            receitaBrutaRaw = parseFloat(receitaBrutaElement.textContent.replace(',', '.')) || 0;
            receitaLiquidaRaw = parseFloat(receitaLiquidaElement.textContent.replace(',', '.')) || 0;
        }
    } catch (e) {
        console.warn('Erro ao parsear dados de receita:', e);
    }
    
    const diferencaDescontos = receitaBrutaRaw - receitaLiquidaRaw;

    new Chart(ctxReceita, {
        type: 'doughnut',
        data: {
            labels: ['Receita Líquida', 'Custos/Descontos'],
            datasets: [{
                data: [receitaLiquidaRaw, diferencaDescontos],
                backgroundColor: ['#27ae60', '#ecf0f1'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 12, padding: 20, usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) label += ': ';
                            label += new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(context.raw);
                            return label;
                        }
                    }
                }
            }
        }
    });
}

