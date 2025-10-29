// static/js/inicio.js - Versão Melhorada

// Função para redirecionar para a página do projeto
function abrirProjeto(idProjeto) {
    window.location.href = `/projeto/${idProjeto}`;
}

// Função para configurar os efeitos interativos nos cards
function configurarCardsInterativos() {
    const cards = document.querySelectorAll('.projeto-card');
    
    cards.forEach(card => {
        // Efeitos de hover melhorados
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
            this.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)';
        });
        
        // Click em qualquer área do card
        card.style.cursor = 'pointer';
        
        // Efeito de clique
        card.addEventListener('click', function(e) {
            if (!e.target.closest('button')) {
                const idProjeto = this.getAttribute('onclick').match(/\d+/)[0];
                abrirProjeto(idProjeto);
            }
        });
    });
}

// Função para animação de entrada dos cards
function animarEntradaCards() {
    const cards = document.querySelectorAll('.projeto-card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Função para carregar estatísticas
function carregarEstatisticas() {
    const projetosCount = document.querySelector('.projetos-count');
    if (projetosCount) {
        const count = projetosCount.textContent.match(/\d+/)[0];
        console.log(`🎯 ${count} projetos carregados com sucesso!`);
    }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    configurarCardsInterativos();
    animarEntradaCards();
    carregarEstatisticas();
});

// Exportar funções para uso global
window.abrirProjeto = abrirProjeto;