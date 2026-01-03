// static/js/main.js
import './modais/estoque.js';

document.addEventListener("DOMContentLoaded", function() {
    
    // Lógica para a tela de NOVA VENDA
    const formVenda = document.getElementById('form-nova-venda');
    if (formVenda) {
        const inputDesconto = document.getElementById('desconto');
        const spanSubtotal = document.getElementById('subtotal');
        const spanTotal = document.getElementById('valor-total');

        // Adiciona ouvintes para recalcular
        inputDesconto.addEventListener('input', calcularTotais);
        
        // Simplesmente para formatar o campo de desconto
        inputDesconto.addEventListener('blur', () => {
             inputDesconto.value = formatarMoeda(parseValor(inputDesconto.value));
        });

        // Placeholder para a função de adicionar produto
        window.adicionarProduto = function() {
            // No mundo real, isso viria do backend após busca
            const produtoMock = {
                id: 1001,
                nome: "Mouse Óptico",
                qtd: parseInt(document.getElementById('qtd-produto').value) || 1,
                valorUnit: 45.00
            };
            
            const tabelaBody = document.getElementById('tabela-itens-venda').querySelector('tbody');
            
            // Remove o placeholder se existir
            const placeholder = document.getElementById('placeholder-carrinho');
            if(placeholder) placeholder.style.display = 'none';

            const newRow = tabelaBody.insertRow();
            newRow.innerHTML = `
                <td>${produtoMock.id}</td>
                <td>${produtoMock.nome}</td>
                <td class="qtd">${produtoMock.qtd}</td>
                <td class="valor-unit">${formatarMoeda(produtoMock.valorUnit)}</td>
                <td class="total-item">${formatarMoeda(produtoMock.qtd * produtoMock.valorUnit)}</td>
                <td><a href="#" onclick="removerItem(this)">Remover</a></td>
            `;
            
            calcularTotais();
        }
        
        // Placeholder para remover item
        window.removerItem = function(button) {
            button.closest('tr').remove();
            calcularTotais();
        }

        // Função principal de cálculo
        function calcularTotais() {
            const tabelaBody = document.getElementById('tabela-itens-venda').querySelector('tbody');
            let subtotal = 0;
            
            tabelaBody.querySelectorAll('tr').forEach(row => {
                const totalItemStr = row.querySelector('.total-item')?.textContent;
                if(totalItemStr) {
                    subtotal += parseValor(totalItemStr);
                }
            });

            const desconto = parseValor(inputDesconto.value);
            const total = subtotal - desconto;
            
            spanSubtotal.textContent = formatarMoeda(subtotal);
            spanTotal.textContent = formatarMoeda(total);
        }
    }

});

/* ----- Funções Utilitárias ----- */

// Converte string (ex: "R$ 1.234,56" ou "1234.56") para float
function parseValor(valorStr) {
    if (typeof valorStr !== 'string') valorStr = String(valorStr);
    return parseFloat(valorStr.replace("R$", "").replace(".", "").replace(",", ".").trim()) || 0;
}

// Formata número para moeda brasileira
function formatarMoeda(valor) {
    return valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}