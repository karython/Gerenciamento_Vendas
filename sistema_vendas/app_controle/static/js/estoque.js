// ============================================
// ESTOQUE.JS - Lógica para página de estoque
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

// Modais
const modalCadastrar = document.getElementById('modal-cadastrar');
const modalEditar = document.getElementById('modal-editar');
const modalReposicao = document.getElementById('modal-reposicao');
const btnCadastrar = document.getElementById('btn-cadastrar-produto');
const btnReposicao = document.getElementById('btn-lancar-reposicao');
const closeBtns = document.querySelectorAll('.close');

btnCadastrar.onclick = () => modalCadastrar.style.display = 'block';
btnReposicao.onclick = () => modalReposicao.style.display = 'block';

closeBtns.forEach(btn => {
    btn.onclick = function() {
        const modal = this.dataset.modal;
        if (modal === 'cadastrar') modalCadastrar.style.display = 'none';
        if (modal === 'editar') modalEditar.style.display = 'none';
        if (modal === 'reposicao') modalReposicao.style.display = 'none';
    }
});

window.onclick = (e) => {
    if (e.target == modalCadastrar) modalCadastrar.style.display = 'none';
    if (e.target == modalEditar) modalEditar.style.display = 'none';
    if (e.target == modalReposicao) modalReposicao.style.display = 'none';
}

// Cadastrar Produto
document.getElementById('form-cadastrar-produto').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const dados = {
        nome: document.getElementById('nome-produto').value,
        preco_custo: parseFloat(document.getElementById('preco-custo').value) || 0,
        preco_venda: parseFloat(document.getElementById('preco-venda').value),
        quantidade_inicial: parseInt(document.getElementById('quantidade-inicial').value),
        is_service: document.getElementById('is-servico').checked
    };
    
    try {
        const response = await fetch("/estoque/cadastrar/", {
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
            location.reload();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao cadastrar produto');
    }
});

// Editar Produto - Abrir Modal
document.addEventListener('click', async function(e) {
    const btnEditar = e.target.closest('.btn-editar');
    
    if (btnEditar) {
        e.preventDefault();
        const produtoId = btnEditar.dataset.id;
        
        try {
            const response = await fetch(`/estoque/buscar/${produtoId}/`);
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('edit-produto-id').value = produtoId;
                document.getElementById('edit-nome-produto').value = result.produto.nome;
                document.getElementById('edit-preco-custo').value = result.produto.preco_custo;
                document.getElementById('edit-preco-venda').value = result.produto.preco_venda;
                document.getElementById('edit-quantidade').value = result.produto.quantidade;
                document.getElementById('edit-is-servico').checked = !!result.produto.is_service;
                
                modalEditar.style.display = 'block';
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao buscar dados do produto');
        }
    }
});

// Editar Produto - Salvar
document.getElementById('form-editar-produto').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const produtoId = document.getElementById('edit-produto-id').value;
    const dados = {
        nome: document.getElementById('edit-nome-produto').value,
        preco_custo: parseFloat(document.getElementById('edit-preco-custo').value),
        preco_venda: parseFloat(document.getElementById('edit-preco-venda').value),
        quantidade: parseInt(document.getElementById('edit-quantidade').value),
        is_service: document.getElementById('edit-is-servico').checked
    };
    
    try {
        const response = await fetch(`/estoque/editar/${produtoId}/`, {
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
            location.reload();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao editar produto');
    }
});

// Deletar Produto
document.addEventListener('click', async function(e) {
    const btnDeletar = e.target.closest('.btn-deletar');
    
    if (btnDeletar) {
        e.preventDefault();
        
        const nomeProduto = btnDeletar.closest('tr').querySelector('td').innerText;
        
        if (!confirm(`Tem certeza que deseja deletar o produto "${nomeProduto}" do estoque?`)) {
            return;
        }
        
        const produtoId = btnDeletar.dataset.id;
        
        try {
            const response = await fetch(`/estoque/deletar/${produtoId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(result.message);
                
                const linha = document.querySelector(`tr[data-produto-id="${produtoId}"]`);
                if(linha) linha.remove();
                
                const tbody = document.getElementById('tabela-estoque');
                if (tbody.children.length === 0) {
                    tbody.innerHTML = '<tr id="linha-vazia"><td colspan="6" style="text-align: center;">Nenhum produto cadastrado</td></tr>';
                }
            } else {
                alert('Erro: ' + result.message);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao deletar produto');
        }
    }
});

// Lançar Reposição
document.getElementById('form-reposicao').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const produtoId = document.getElementById('produto-reposicao').value;
    const quantidade = parseInt(document.getElementById('quantidade-reposicao').value);
    
    try {
        const response = await fetch(`/estoque/reposicao/${produtoId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ quantidade })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            
            const linha = document.querySelector(`tr[data-produto-id="${produtoId}"]`);
            if (linha) {
                linha.querySelector('.quantidade').textContent = result.nova_quantidade;
            }
            
            modalReposicao.style.display = 'none';
            this.reset();
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao adicionar reposição');
    }
});