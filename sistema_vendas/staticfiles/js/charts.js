// static/js/charts.js
// Este script só é carregado na página do Dashboard

document.addEventListener("DOMContentLoaded", function() {
    
    // --- Gráfico 1: Vendas por Dia (Linha) ---
    const ctxVendas = document.getElementById('graficoVendas');
    if (ctxVendas) {
        // Dados de exemplo (viriam do backend)
        const labels = ['Dia 1', 'Dia 2', 'Dia 3', 'Dia 4', 'Dia 5', 'Dia 6', 'Dia 7'];
        const data = {
            labels: labels,
            datasets: [{
                label: 'Vendas Realizadas',
                data: [12, 19, 3, 5, 2, 3, 9], // Dados de exemplo
                fill: false,
                borderColor: 'rgb(13, 110, 253)', // Cor --cor-primaria
                tension: 0.1
            }]
        };

        new Chart(ctxVendas, {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // --- Gráfico 2: Receita (Barra) ---
    const ctxReceita = document.getElementById('graficoReceita');
    if (ctxReceita) {
        // Dados de exemplo (viriam do backend)
        const labelsReceita = ['Outubro', 'Novembro', 'Dezembro'];
        const dataReceita = {
            labels: labelsReceita,
            datasets: [
                {
                    label: 'Receita Bruta',
                    data: [15780, 18200, 14100], // Dados de exemplo
                    backgroundColor: 'rgba(13, 110, 253, 0.7)', // Cor --cor-primaria (com transparência)
                },
                {
                    label: 'Receita Líquida',
                    data: [12120, 14500, 11300], // Dados de exemplo
                    backgroundColor: 'rgba(25, 135, 84, 0.7)', // Cor --cor-sucesso (com transparência)
                }
            ]
        };

        new Chart(ctxReceita, {
            type: 'bar',
            data: dataReceita,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
});