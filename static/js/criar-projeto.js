// criar-projeto.js
document.addEventListener('DOMContentLoaded', function() {
    const nomeInput = document.getElementById('nome_projeto');
    const descricaoTextarea = document.getElementById('descricao_projeto');
    const nomeCounter = nomeInput?.parentElement.querySelector('.char-count');
    const descricaoCounter = descricaoTextarea?.parentElement.querySelector('.char-count');
    
    // Atualizar contadores
    function updateCounter(input, counter, maxLength) {
        if (input && counter) {
            const length = input.value.length;
            counter.textContent = `${length}/${maxLength}`;
            
            // Altera cor se estiver perto do limite
            if (length > maxLength * 0.8) {
                counter.style.color = '#e74c3c';
            } else {
                counter.style.color = '#7f8c8d';
            }
        }
    }
    
    // Event listeners
    if (nomeInput && nomeCounter) {
        nomeInput.addEventListener('input', function() {
            updateCounter(nomeInput, nomeCounter, 100);
        });
        updateCounter(nomeInput, nomeCounter, 100); // Inicial
    }
    
    if (descricaoTextarea && descricaoCounter) {
        descricaoTextarea.addEventListener('input', function() {
            updateCounter(descricaoTextarea, descricaoCounter, 500);
        });
        updateCounter(descricaoTextarea, descricaoCounter, 500); // Inicial
    }
    
    // Validação do formulário
    const form = document.querySelector('.projeto-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const nome = nomeInput?.value.trim();
            
            if (!nome) {
                e.preventDefault();
                alert('Por favor, insira um nome para o projeto.');
                nomeInput?.focus();
            }
        });
    }
});