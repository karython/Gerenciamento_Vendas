// ============================================
// CLIENTES.JS - Lógica para página de clientes
// ============================================

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

document.getElementById('form-novo-cliente').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const csrfToken = getCookie('csrftoken');
    
    fetch(window.clientesUrls.criar, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            
            const linhaVazia = document.getElementById('linha-vazia');
            if (linhaVazia) linhaVazia.remove();
            
            const tbody = document.getElementById('tabela-clientes');
            const novaLinha = document.createElement('tr');
            novaLinha.setAttribute('data-cliente-id', data.cliente.id);
            
            novaLinha.innerHTML = `
                <td>${data.cliente.nome}</td>
                <td>${data.cliente.cpf}</td>
                <td>${data.cliente.telefone}</td>
                <td style="text-align: center;">
                    <a href="${window.clientesUrls.editar}${data.cliente.id}/" class="btn-acao btn-editar" title="Editar">
                        <i class="fas fa-edit"></i>
                    </a>
                    <button class="btn-acao btn-deletar" data-id="${data.cliente.id}" title="Deletar">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            
            tbody.insertBefore(novaLinha, tbody.firstChild);
            
            document.getElementById('form-novo-cliente').reset();
            document.querySelector('.accordion details').removeAttribute('open');
            
        } else {
            alert('Erro: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cadastrar cliente.');
    });
});

document.addEventListener('click', function(e) {
    const btnDeletar = e.target.closest('.btn-deletar');
    
    if (btnDeletar) {
        e.preventDefault();
        
        const row = btnDeletar.closest('tr');
        const nomeCliente = row.cells[0].innerText;
        
        if (confirm(`Tem certeza que deseja excluir o cliente "${nomeCliente}"?`)) {
            const clienteId = btnDeletar.dataset.id;
            const csrfToken = getCookie('csrftoken');
            
            fetch(`${window.clientesUrls.deletar}${clienteId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    row.remove();
                    
                    const tbody = document.getElementById('tabela-clientes');
                    if (tbody.children.length === 0) {
                        tbody.innerHTML = '<tr id="linha-vazia"><td colspan="4" style="text-align: center;">Nenhum cliente cadastrado</td></tr>';
                    }
                } else {
                    if (data.has_vendas) {
                        alert(
                            `❌ NÃO É POSSÍVEL EXCLUIR!\n\n` +
                            `O cliente possui ${data.quantidade_vendas} venda(s) registrada(s).\n` +
                            `Você precisa excluir as vendas deste cliente antes de removê-lo.`
                        );
                    } else {
                        alert(`❌ ${data.message}`);
                    }
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao deletar cliente');
            });
        }
    }
});