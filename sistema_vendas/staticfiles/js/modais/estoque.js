
    // ========== DADOS DE EXEMPLO ==========
    const produtos = [
        { id: 1, codigo: 'PROD001', nome: 'Notebook Dell Inspiron', custo: 2500.00 },
        { id: 2, codigo: 'PROD002', nome: 'Mouse Logitech MX Master', custo: 350.00 },
        { id: 3, codigo: 'PROD003', nome: 'Teclado Mecânico Keychron', custo: 450.00 },
        { id: 4, codigo: 'PROD004', nome: 'Monitor LG 27 4K', custo: 1800.00 },
        { id: 5, codigo: 'PROD005', nome: 'Webcam Logitech C920', custo: 450.00 },
        { id: 6, codigo: 'PROD006', nome: 'Headset HyperX Cloud', custo: 320.00 },
        { id: 7, codigo: 'PROD007', nome: 'SSD Samsung 1TB', custo: 550.00 },
        { id: 8, codigo: 'PROD008', nome: 'Memória RAM 16GB DDR4', custo: 280.00 }
    ];

    // ========== MODAL NOVO PRODUTO ==========
    const novoProdutoModal = document.getElementById('novoProdutoModal');
    const openNovoProduto = document.getElementById('openNovoProduto');
    const closeNovoProduto = document.getElementById('closeNovoProduto');
    const cancelNovoProduto = document.getElementById('cancelNovoProduto');
    const formNovoProduto = document.getElementById('formNovoProduto');

    function openModalNovoProduto() {
        novoProdutoModal.classList.add('active');
        novoProdutoModal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeModalNovoProduto() {
        novoProdutoModal.classList.remove('active');
        novoProdutoModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        formNovoProduto.reset();
    }

    openNovoProduto?.addEventListener('click', openModalNovoProduto);
    closeNovoProduto?.addEventListener('click', closeModalNovoProduto);
    cancelNovoProduto?.addEventListener('click', closeModalNovoProduto);

    novoProdutoModal?.addEventListener('click', (e) => {
        if (e.target === novoProdutoModal) closeModalNovoProduto();
    });

    formNovoProduto?.addEventListener('submit', function(e) {
        const nome = document.getElementById('nome_produto_novo').value.trim();
        const valor = document.getElementById('valor_unitario').value;
        
        if (!nome) {
            e.preventDefault();
            alert('Informe o nome do produto.');
            return;
        }
        if (valor === '' || isNaN(parseFloat(valor)) || parseFloat(valor) < 0) {
            e.preventDefault();
            alert('Informe um valor unitário válido.');
            return;
        }
    });

    // ========== MODAL REPOSIÇÃO ==========
    const reposicaoModal = document.getElementById('reposicaoModal');
    const openReposicao = document.getElementById('openReposicao');
    const closeReposicao = document.getElementById('closeReposicao');
    const cancelReposicao = document.getElementById('cancelReposicao');
    const formReposicao = document.getElementById('formReposicao');

    const searchInput = document.getElementById('search_produto');
    const selectProduto = document.getElementById('select_produto');
    const productInfo = document.getElementById('product_info');

    const nomeProduto = document.getElementById('nome_produto');
    const precoCusto = document.getElementById('preco_custo');
    const precoVenda = document.getElementById('preco_venda');
    const quantidade = document.getElementById('quantidade');

    const infoNome = document.getElementById('info_nome');
    const infoCodigo = document.getElementById('info_codigo');


    function formatCurrency(value) {
        return value.toFixed(2).replace('.', ',');
    }

    function populateProducts(filter = '') {
        const filterLower = filter.toLowerCase();
        const filtered = produtos.filter(p => 
            p.nome.toLowerCase().includes(filterLower) || 
            p.codigo.toLowerCase().includes(filterLower)
        );

        selectProduto.innerHTML = '<option value="">Selecione um produto...</option>';
        
        filtered.forEach(produto => {
            const option = document.createElement('option');
            option.value = produto.id;
            option.textContent = `${produto.codigo} - ${produto.nome}`;
            option.dataset.produto = JSON.stringify(produto);
            selectProduto.appendChild(option);
        });
    }

    function clearFormReposicao() {
        formReposicao.reset();
        nomeProduto.value = '';
        precoCusto.value = '';
        productInfo.classList.remove('active');
        populateProducts();
    }

    function openModalReposicao() {
        reposicaoModal.classList.add('active');
        reposicaoModal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        populateProducts();
    }

    function closeModalReposicao() {
        reposicaoModal.classList.remove('active');
        reposicaoModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        clearFormReposicao();
    }

    openReposicao?.addEventListener('click', openModalReposicao);
    closeReposicao?.addEventListener('click', closeModalReposicao);
    cancelReposicao?.addEventListener('click', closeModalReposicao);

    reposicaoModal?.addEventListener('click', (e) => {
        if (e.target === reposicaoModal) closeModalReposicao();
    });

    searchInput?.addEventListener('input', (e) => {
        populateProducts(e.target.value);
    });

    selectProduto?.addEventListener('change', (e) => {
        const option = e.target.selectedOptions[0];
        if (!option || !option.dataset.produto) {
            productInfo.classList.remove('active');
            nomeProduto.value = '';
            precoCusto.value = '';
            return;
        }

        const produto = JSON.parse(option.dataset.produto);
        
        nomeProduto.value = produto.nome;
        precoCusto.value = formatCurrency(produto.custo);
        
        infoNome.textContent = produto.nome;
        infoCodigo.textContent = produto.codigo;
        infoCusto.textContent = formatCurrency(produto.custo);
        productInfo.classList.add('active');

        precoVenda.focus();
    });

    formReposicao?.addEventListener('submit', (e) => {
        e.preventDefault();

        const produtoId = selectProduto.value;
        const produtoNome = nomeProduto.value;
        const custoValue = precoCusto.value;
        const vendaValue = precoVenda.value;
        const qtdValue = quantidade.value;

        if (!produtoId) {
            alert('Por favor, selecione um produto.');
            return;
        }

        if (!vendaValue || parseFloat(vendaValue) <= 0) {
            alert('Por favor, informe um preço de venda válido.');
            precoVenda.focus();
            return;
        }

        if (!qtdValue || parseInt(qtdValue) < 1) {
            alert('Por favor, informe uma quantidade válida.');
            quantidade.focus();
            return;
        }

        const dados = {
            produto_id: produtoId,
            produto_nome: produtoNome,
            preco_custo: custoValue,
            preco_venda: parseFloat(vendaValue),
            quantidade: parseInt(qtdValue)
        };

        console.log('Dados da reposição:', dados);
        
        alert(`Reposição confirmada!\n\nProduto: ${dados.produto_nome}\nQuantidade: ${dados.quantidade}\nPreço de Venda: R$ ${formatCurrency(dados.preco_venda)}`);
        
        closeModalReposicao();

        // Integração com backend:
        // fetch('/api/reposicao', {
        //     method: 'POST',
        //     headers: { 
        //         'Content-Type': 'application/json',
        //         'X-CSRFToken': '{{ csrf_token }}'
        //     },
        //     body: JSON.stringify(dados)
        // }).then(response => response.json())
        //   .then(data => { 
        //       alert('Reposição salva com sucesso!');
        //       closeModalReposicao();
        //   })
        //   .catch(error => {
        //       alert('Erro ao salvar reposição');
        //       console.error(error);
        //   });
    });

    // ========== FECHAR MODAIS COM ESC ==========
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (novoProdutoModal?.classList.contains('active')) {
                closeModalNovoProduto();
            }
            if (reposicaoModal?.classList.contains('active')) {
                closeModalReposicao();
            }
        }
    });
