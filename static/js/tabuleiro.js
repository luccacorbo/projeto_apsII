// Configurações do tabuleiro
const config = {
    totalCasas: 100,
    casasPorLinha: 10,
    posicaoJogador: window.posicaoAtual || 0,
    jogadorElement: null,
    nomeElement: null,
    saldo: window.saldo || 0
};

// Inicialização do tabuleiro
document.addEventListener('DOMContentLoaded', function() {
    inicializarTabuleiro();
    atualizarInfoJogador();
    atualizarSaldo();
    carregarUsuariosOnline();
    carregarRecompensasGanhas();
    
    // Adiciona event listeners para modais
    inicializarModais();
});

// Inicializa os modais com correções
function inicializarModais() {
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharTodosModais();
        }
    });

    // Fechar modal clicando fora - CORREÇÃO APLICADA
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            fecharModalPorElemento(e.target);
        }
    });

    // Prevenir fechamento ao clicar dentro do conteúdo do modal
    document.querySelectorAll('.modal-content, .modal-card').forEach(conteudo => {
        conteudo.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Garantir que os botões de fechar modal funcionem corretamente
    document.querySelectorAll('.modal .close, [onclick*="fecharModal"]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = this.closest('.modal');
            if (modal) {
                fecharModalPorElemento(modal);
            }
        });
    });
}

// Inicializa o tabuleiro com todas as casas
function inicializarTabuleiro() {
    const tabuleiro = document.getElementById('tabuleiro');
    const totalLinhas = Math.ceil(config.totalCasas / config.casasPorLinha);
    
    // Limpa o tabuleiro
    tabuleiro.innerHTML = '';
    
    // Cria as linhas e casas
    for (let i = 0; i < totalLinhas; i++) {
        const linha = document.createElement('div');
        linha.className = `linha ${i % 2 === 1 ? 'invertida' : ''}`;
        
        const inicio = i * config.casasPorLinha;
        const fim = Math.min(inicio + config.casasPorLinha, config.totalCasas);
        
        for (let j = inicio; j < fim; j++) {
            const casa = criarCasa(j + 1);
            linha.appendChild(casa);
        }
        
        tabuleiro.appendChild(linha);
    }
    
    // Adiciona recompensas
    adicionarRecompensas();
    
    // Cria caminhos entre as casas
    criarCaminhos();
    
    // Posiciona o jogador na posição atual
    posicionarJogador(config.posicaoJogador);
}

// Cria uma casa individual
function criarCasa(numero) {
    const casa = document.createElement('div');
    casa.className = 'casa';
    casa.textContent = numero;
    casa.dataset.numero = numero;
    casa.dataset.casaId = numero;
    
    // Adiciona evento de clique para todas as casas
    casa.addEventListener('click', function() {
        mostrarInfoCasa(numero);
    });
    
    // Casa inicial
    if (numero === 1) {
        casa.classList.add('casa-start');
    }
    
    // Casa final
    if (numero === config.totalCasas) {
        casa.classList.add('casa-finish');
    }
    
    return casa;
}

// Mostra informações da casa ao clicar
function mostrarInfoCasa(numero) {
    const casa = document.querySelector(`.casa[data-numero="${numero}"]`);
    const recompensa = window.recompensas ? window.recompensas.find(r => r.posicao === numero) : null;
    
    document.getElementById('casa-titulo').textContent = recompensa ? recompensa.titulo : `Casa ${numero}`;
    document.getElementById('casa-numero').textContent = `Posição: ${numero}`;
    
    if (recompensa) {
        document.getElementById('casa-descricao').textContent = recompensa.descricao;
    } else {
        document.getElementById('casa-descricao').textContent = 
            'Esta é uma casa comum do tabuleiro. Avance para descobrir recompensas!';
    }
    
    abrirModal('casa-info');
}

// Funções para criador
function editarRecompensaCasa() {
    const numeroCasa = document.getElementById('casa-numero').textContent.split(': ')[1];
    // Implementar lógica para editar recompensa
    console.log(`Editar recompensa da casa ${numeroCasa}`);
    fecharModal('casa-info');
    abrirModal('editar');
}

function adicionarRecompensaCasa() {
    const numeroCasa = document.getElementById('casa-numero').textContent.split(': ')[1];
    // Implementar lógica para adicionar recompensa
    console.log(`Adicionar recompensa à casa ${numeroCasa}`);
    fecharModal('casa-info');
    abrirModal('adicionar');
}

// Cria caminhos estilizados entre as casas
function criarCaminhos() {
    const tabuleiro = document.getElementById('tabuleiro');
    const linhas = tabuleiro.querySelectorAll('.linha');
    
    linhas.forEach((linha, index) => {
        const casas = linha.querySelectorAll('.casa');
        
        // Caminhos horizontais entre casas
        for (let i = 0; i < casas.length - 1; i++) {
            const casa1 = casas[i];
            const casa2 = casas[i + 1];
            
            const rect1 = casa1.getBoundingClientRect();
            const rect2 = casa2.getBoundingClientRect();
            const tabuleiroRect = tabuleiro.getBoundingClientRect();
            
            const caminhoHorizontal = document.createElement('div');
            caminhoHorizontal.className = 'caminho-horizontal';
            
            const x1 = rect1.right - tabuleiroRect.left;
            const x2 = rect2.left - tabuleiroRect.left;
            const y = rect1.top - tabuleiroRect.top + rect1.height / 2;
            
            caminhoHorizontal.style.left = `${x1}px`;
            caminhoHorizontal.style.top = `${y}px`;
            caminhoHorizontal.style.width = `${x2 - x1}px`;
            
            tabuleiro.appendChild(caminhoHorizontal);
        }
        
        // Caminhos verticais entre linhas (exceto última linha)
        if (index < linhas.length - 1) {
            const proximaLinha = linhas[index + 1];
            const ultimaCasa = casas[casas.length - 1];
            const primeiraProximaCasa = proximaLinha.querySelector('.casa');
            
            const rect1 = ultimaCasa.getBoundingClientRect();
            const rect2 = primeiraProximaCasa.getBoundingClientRect();
            const tabuleiroRect = tabuleiro.getBoundingClientRect();
            
            const caminhoVertical = document.createElement('div');
            caminhoVertical.className = 'caminho-vertical';
            
            const x = rect1.left - tabuleiroRect.left + rect1.width / 2;
            const y1 = rect1.bottom - tabuleiroRect.top;
            const y2 = rect2.top - tabuleiroRect.top;
            
            caminhoVertical.style.left = `${x}px`;
            caminhoVertical.style.top = `${y1}px`;
            caminhoVertical.style.height = `${y2 - y1}px`;
            
            tabuleiro.appendChild(caminhoVertical);
        }
    });
}

// Adiciona recompensas ao tabuleiro
function adicionarRecompensas() {
    if (!window.recompensas) return;
    
    window.recompensas.forEach(recompensa => {
        const casa = document.querySelector(`.casa[data-numero="${recompensa.posicao}"]`);
        if (casa) {
            casa.classList.add('recompensa');
            casa.innerHTML = `
                <div class="gift">🎁</div>
                <div class="rec-nome" title="${recompensa.titulo} - ${recompensa.descricao}">${recompensa.titulo}</div>
                <div class="num">${recompensa.posicao}</div>
            `;
            casa.dataset.recompensaId = recompensa.id_recompensa;
            casa.dataset.recompensaTitulo = recompensa.titulo;
            casa.dataset.recompensaDescricao = recompensa.descricao;
        }
    });
}

// Carrega usuários online do projeto
function carregarUsuariosOnline() {
    const listaUsuarios = document.getElementById('lista-usuarios');
    
    if (!window.usuariosOnline || window.usuariosOnline.length === 0) {
        listaUsuarios.innerHTML = '<div class="sem-dados">Nenhum membro encontrado</div>';
        return;
    }
    
    listaUsuarios.innerHTML = '';
    window.usuariosOnline.forEach(usuario => {
        const usuarioItem = document.createElement('div');
        usuarioItem.className = 'usuario-item';
        usuarioItem.innerHTML = `
            <span class="usuario-nome">${usuario.nome}</span>
            <span class="usuario-posicao">Pos: ${usuario.posicao_atual || 0}</span>
            <span class="usuario-saldo">Saldo: ${usuario.saldo || 0}</span>
        `;
        listaUsuarios.appendChild(usuarioItem);
    });
}

// Carrega recompensas ganhas
function carregarRecompensasGanhas() {
    const gridRecompensas = document.getElementById('grid-recompensas');
    
    if (!window.recompensasGanhas || window.recompensasGanhas.length === 0) {
        gridRecompensas.innerHTML = '<div class="sem-dados">Nenhuma recompensa conquistada ainda</div>';
        return;
    }
    
    gridRecompensas.innerHTML = '';
    window.recompensasGanhas.forEach(recompensa => {
        const card = document.createElement('div');
        card.className = 'card-recompensa';
        card.innerHTML = `
            <div class="recompensa-titulo">${recompensa.titulo}</div>
            <div class="recompensa-descricao">${recompensa.descricao}</div>
            <div class="recompensa-info">
                <span>Conquistada em: ${new Date(recompensa.data_conquista).toLocaleDateString('pt-BR')}</span>
                <span>Casa: ${recompensa.posicao}</span>
            </div>
        `;
        gridRecompensas.appendChild(card);
    });
}

// Atualiza informações do jogador no painel lateral
function atualizarInfoJogador() {
    document.getElementById('nome-jogador-display').textContent = window.nomeJogador;
    document.getElementById('posicao-atual').textContent = config.posicaoJogador + 1;
}

// Atualiza o saldo e controla o estado do botão
function atualizarSaldo() {
    const saldoElement = document.getElementById('saldo-valor');
    const btnGirar = document.getElementById('btnGirarDado');
    const dado = document.getElementById('dado');
    
    saldoElement.textContent = config.saldo;
    
    if (config.saldo === 0) {
        saldoElement.classList.add('zero');
        btnGirar.disabled = true;
        dado.classList.add('disabled');
    } else {
        saldoElement.classList.remove('zero');
        btnGirar.disabled = false;
        dado.classList.remove('disabled');
    }
}

// Adiciona saldo (quando completa tarefa)
function adicionarSaldo(valor) {
    config.saldo += valor;
    atualizarSaldo();
}

// Remove saldo (quando rola o dado)
function removerSaldo(valor) {
    config.saldo -= valor;
    if (config.saldo < 0) config.saldo = 0;
    atualizarSaldo();
}

// Posiciona o jogador em uma casa específica - COM EMOJI DE LOCALIZAÇÃO
function posicionarJogador(novaPosicao) {
    // Remove jogador da posição anterior
    if (config.jogadorElement) {
        config.jogadorElement.remove();
        config.nomeElement.remove();
    }
    
    // Atualiza posição
    config.posicaoJogador = novaPosicao;
    const casa = document.querySelector(`.casa[data-numero="${novaPosicao + 1}"]`);
    
    if (casa) {
        // Marca casa como visitada
        casa.classList.add('visitada');
        
        // Cria elemento do jogador - EMOJI DE LOCALIZAÇÃO
        config.jogadorElement = document.createElement('div');
        config.jogadorElement.className = 'boneco';
        config.jogadorElement.textContent = '🧑‍💼';
        
        // Cria elemento do nome
        config.nomeElement = document.createElement('div');
        config.nomeElement.className = 'nome-jogador';
        config.nomeElement.textContent = window.nomeJogador;
        
        // Adiciona à casa
        casa.appendChild(config.jogadorElement);
        casa.appendChild(config.nomeElement);
    }
    
    // Atualiza informações no painel lateral
    atualizarInfoJogador();
    
    // Verifica se chegou ao final
    if (novaPosicao + 1 === config.totalCasas) {
        setTimeout(() => {
            mostrarMensagemVitoria("🎉 Parabéns! Você chegou ao final do tabuleiro!");
            document.getElementById('btnRecomecar').style.display = 'block';
        }, 500);
    }
}

// Rola o dado e move o jogador - AGORA COM INTEGRAÇÃO COM API
function rolarDado() {
    if (config.saldo <= 0) return;
    
    const dado = document.getElementById('dado');
    const resultadoElem = document.getElementById('res-num');
    const btnGirar = document.getElementById('btnGirarDado');
    
    // Animação de rolagem
    dado.classList.add('rolling');
    dado.textContent = '...';
    resultadoElem.textContent = '...';
    
    // Desabilita o botão durante a rolagem
    btnGirar.disabled = true;
    btnGirar.textContent = '🎲 Rolando...';
    
    // Chamada para a API para girar o dado
    fetch(`/tabuleiro/projeto/${window.idProjeto}/girar_dado`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Atualiza interface com resultado real
            dado.textContent = data.resultado_dado;
            resultadoElem.textContent = data.resultado_dado;
            dado.classList.remove('rolling');
            
            // Atualiza saldo
            config.saldo = data.saldo_restante;
            atualizarSaldo();
            
            // Move o jogador
            moverJogador(data.resultado_dado);
            
            // Se ganhou recompensa, mostra mensagem
            if (data.recompensa) {
                setTimeout(() => {
                    mostrarMensagemRecompensa(data.recompensa.titulo, data.recompensa.descricao);
                }, 500);
            }
        } else {
            alert('Erro: ' + data.error);
            dado.textContent = '–';
            resultadoElem.textContent = '–';
            dado.classList.remove('rolling');
        }
        
        // Reabilita o botão
        btnGirar.disabled = config.saldo <= 0;
        btnGirar.textContent = '🎲 Girar Dado';
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao girar dado');
        dado.textContent = '–';
        resultadoElem.textContent = '–';
        dado.classList.remove('rolling');
        btnGirar.disabled = false;
        btnGirar.textContent = '🎲 Girar Dado';
    });
}

// Move o jogador pelas casas
function moverJogador(passos) {
    let novaPosicao = config.posicaoJogador + passos;
    
    // Não ultrapassa o final
    if (novaPosicao >= config.totalCasas) {
        novaPosicao = config.totalCasas - 1;
    }
    
    // Animação de movimento
    moverPassoAPasso(config.posicaoJogador, novaPosicao);
}

// Move o jogador passo a passo com animação
function moverPassoAPasso(de, para) {
    let posicaoAtual = de;
    
    const intervalo = setInterval(() => {
        posicaoAtual++;
        posicionarJogador(posicaoAtual);
        
        // Verifica recompensa localmente (para animação)
        verificarRecompensaLocal(posicaoAtual);
        
        if (posicaoAtual >= para) {
            clearInterval(intervalo);
        }
    }, 300);
}

// Verifica se o jogador caiu em uma recompensa (apenas para animação)
function verificarRecompensaLocal(posicao) {
    const casa = document.querySelector(`.casa[data-numero="${posicao + 1}"]`);
    
    if (casa && casa.classList.contains('recompensa')) {
        const titulo = casa.dataset.recompensaTitulo;
        const descricao = casa.dataset.recompensaDescricao;
        
        // Apenas para efeito visual - o saldo real já foi atualizado pela API
        setTimeout(() => {
            mostrarMensagemRecompensa(titulo, descricao);
        }, 500);
    }
}

// Mostra mensagem de recompensa personalizada
function mostrarMensagemRecompensa(titulo, descricao) {
    const mensagens = [
        "🎉 Excelente! Você encontrou uma recompensa!",
        "🌟 Que sorte! Uma recompensa especial!",
        "💫 Incrível! Mais uma conquista no seu caminho!",
        "🔥 Fantástico! Recompensa desbloqueada!",
        "🚀 Você está voando! Nova recompensa adquirida!"
    ];
    
    const mensagemAleatoria = mensagens[Math.floor(Math.random() * mensagens.length)];
    
    document.getElementById('textoRecompensa').textContent = mensagemAleatoria;
    document.getElementById('saldo-ganho').textContent = "+5 de saldo!";
    document.getElementById('mensagem-recompensa').textContent = 
        `Você ganhou: "${titulo}" - ${descricao}`;
    
    abrirModal('ganhou');
}

// Mostra mensagem de vitória personalizada
function mostrarMensagemVitoria(mensagem) {
    document.getElementById('textoRecompensa').textContent = mensagem;
    document.getElementById('saldo-ganho').textContent = "🎊 Missão Cumprida!";
    document.getElementById('mensagem-recompensa').textContent = 
        "Você completou todo o tabuleiro! Parabéns pela conquista!";
    
    abrirModal('ganhou');
}

// ================================
// FUNÇÕES DE MODAL CORRIGIDAS - POSICIONAMENTO DINÂMICO
// ================================

// Função para abrir modal - CORREÇÃO APLICADA (posicionamento inteligente)
function abrirModal(tipo) {
    const modal = document.getElementById(`modal-${tipo}`);
    if (modal) {
        // Remove qualquer posicionamento anterior
        modal.style.alignItems = '';
        modal.style.paddingTop = '';
        modal.style.paddingBottom = '';
        
        modal.classList.add('show');
        document.body.classList.add('modal-open');
        
        // Posiciona o modal de forma inteligente baseado na posição de scroll
        setTimeout(() => {
            posicionarModalInteligente(modal);
        }, 10);
        
        // Garantir que o modal seja rolável se necessário
        setTimeout(() => {
            modal.scrollTop = 0;
        }, 10);
    }
}

// Nova função para posicionar modal de forma inteligente
function posicionarModalInteligente(modal) {
    const modalContent = modal.querySelector('.modal-content') || modal.querySelector('.modal-card') || modal;
    const viewportHeight = window.innerHeight;
    const scrollY = window.scrollY;
    const modalHeight = modalContent.offsetHeight;
    
    // Calcula a posição visível atual
    const visibleAreaTop = scrollY;
    const visibleAreaBottom = scrollY + viewportHeight;
    
    // Se o modal for maior que 80% da viewport, usa scroll interno
    if (modalHeight > viewportHeight * 0.8) {
        modal.style.alignItems = 'flex-start';
        modal.style.paddingTop = '20px';
        modal.style.paddingBottom = '20px';
        modalContent.style.maxHeight = '90vh';
    } else {
        // Para modais menores, posiciona de forma inteligente
        const spaceAbove = visibleAreaTop;
        const spaceBelow = document.documentElement.scrollHeight - visibleAreaBottom;
        
        if (spaceAbove > spaceBelow && spaceAbove > 100) {
            // Mais espaço acima - posiciona mais para cima
            modal.style.alignItems = 'flex-start';
            modal.style.paddingTop = '40px';
        } else if (spaceBelow > spaceAbove && spaceBelow > 100) {
            // Mais espaço abaixo - posiciona mais para baixo
            modal.style.alignItems = 'flex-end';
            modal.style.paddingBottom = '40px';
        } else {
            // Espaço balanceado - centraliza normalmente
            modal.style.alignItems = 'center';
        }
    }
}

// Função para fechar modal - CORREÇÃO APLICADA
function fecharModal(tipo) {
    const modal = document.getElementById(`modal-${tipo}`);
    if (modal) {
        // Reseta estilos de posicionamento
        modal.style.alignItems = '';
        modal.style.paddingTop = '';
        modal.style.paddingBottom = '';
        
        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }
}

// Nova função para fechar modal por elemento
function fecharModalPorElemento(modalElement) {
    // Reseta estilos de posicionamento
    modalElement.style.alignItems = '';
    modalElement.style.paddingTop = '';
    modalElement.style.paddingBottom = '';
    
    modalElement.classList.remove('show');
    document.body.classList.remove('modal-open');
}

// Nova função para fechar todos os modais
function fecharTodosModais() {
    document.querySelectorAll('.modal.show').forEach(modal => {
        modal.style.alignItems = '';
        modal.style.paddingTop = '';
        modal.style.paddingBottom = '';
        modal.classList.remove('show');
    });
    document.body.classList.remove('modal-open');
}

// Confirmação de exclusão
function confirmarExclusao(id) {
    const form = document.getElementById('form-excluir');
    form.action = `{{ url_for('tabuleiro.excluir_recompensa', id_projeto=0, id_recompensa=0) }}`
        .replace('/0/', `/${window.idProjeto}/`)
        .replace('id_recompensa=0', `id_recompensa=${id}`);
    abrirModal('confirmacao');
}

// Recomeçar jogo
function recomecar() {
    if (confirm('Tem certeza que deseja recomeçar o jogo?')) {
        // Remove marcações de casas visitadas
        document.querySelectorAll('.casa.visitada').forEach(casa => {
            casa.classList.remove('visitada');
        });
        
        // Remove jogador
        if (config.jogadorElement) {
            config.jogadorElement.remove();
            config.nomeElement.remove();
            config.jogadorElement = null;
            config.nomeElement = null;
        }
        
        // Reposiciona jogador no início
        config.posicaoJogador = 0;
        posicionarJogador(0);
        
        // Reseta saldo
        config.saldo = 0;
        atualizarSaldo();
        
        // Esconde botão recomeçar
        document.getElementById('btnRecomecar').style.display = 'none';
        
        // Reseta o dado
        document.getElementById('dado').textContent = '–';
        document.getElementById('res-num').textContent = '–';
        
        // TODO: Chamar API para resetar progresso no servidor
    }
}

// Voltar para o projeto
function voltarParaProjeto() {
    window.location.href = `/projeto/${window.idProjeto}`;
}