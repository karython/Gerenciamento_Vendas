/**
 * Sistema de Loader Global
 * Gerencia o loader overlay para requisições AJAX e operações que demoram
 */

let loaderInicializado = false;
let loaderAtivo = false;
let tempoMinimoLoader = 500; // Mínimo 500ms para o loader ficar visível

// Criar overlay de loader se não existir
function inicializarLoader() {
    if (!loaderInicializado && !document.getElementById('loader')) {
        const loaderHTML = `
            <div class="loader-overlay" id="loader">
                <div>
                    <div class="loader-spinner"></div>
                    <div class="loader-text">Processando...</div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('afterbegin', loaderHTML);
        loaderInicializado = true;
        console.log('[Loader] Inicializado com sucesso');
    }
}

// Mostrar loader
function mostrarLoader(mensagem = 'Processando...') {
    inicializarLoader();
    const loader = document.getElementById('loader');
    const loaderText = document.querySelector('.loader-text');
    if (loader && loaderText) {
        loaderText.textContent = mensagem;
        loader.classList.add('active');
        loaderAtivo = true;
        console.log('[Loader] Mostrando:', mensagem);
    }
}

// Ocultar loader
function ocultarLoader() {
    const loader = document.getElementById('loader');
    if (loader && loaderAtivo) {
        setTimeout(() => {
            loader.classList.remove('active');
            loaderAtivo = false;
            console.log('[Loader] Oculto');
        }, tempoMinimoLoader);
    }
}

// Wrapper para fetch com loader automático
async function fetchComLoader(url, opcoes = {}, mensagem = 'Processando...') {
    mostrarLoader(mensagem);
    const inicioCarregamento = Date.now();
    try {
        const resposta = await fetch(url, opcoes);
        return resposta;
    } finally {
        const tempoDecorrido = Date.now() - inicioCarregamento;
        const tempoAguardar = Math.max(0, tempoMinimoLoader - tempoDecorrido);
        setTimeout(ocultarLoader, tempoAguardar);
    }
}

// Interceptar todas as requisições fetch globalmente
const fetchOriginal = window.fetch;
window.fetch = function(...args) {
    // Mostrar loader em requisições POST, PUT, DELETE
    const opcoes = args[1] || {};
    const metodo = (opcoes.method || 'GET').toUpperCase();
    
    if (['POST', 'PUT', 'DELETE'].includes(metodo)) {
        mostrarLoader(opcoes.loaderMensagem || 'Processando...');
        const inicioCarregamento = Date.now();
        
        return fetchOriginal.apply(this, args).finally(() => {
            const tempoDecorrido = Date.now() - inicioCarregamento;
            const tempoAguardar = Math.max(0, tempoMinimoLoader - tempoDecorrido);
            setTimeout(ocultarLoader, tempoAguardar);
        });
    }
    
    return fetchOriginal.apply(this, args);
};

// Inicializar quando o documento estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarLoader);
} else {
    // Página já carregada, inicializar imediatamente
    inicializarLoader();
}

// Expor funções globalmente para teste
window.testarLoader = function() {
    mostrarLoader('Teste de Loader!');
    setTimeout(ocultarLoader, 2000);
    console.log('[Loader] Teste iniciado - o loader deve desaparecer em 2 segundos');
};
