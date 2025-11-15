// Configurações do tabuleiro
const config = {
    totalCasas: 100,
    casasPorLinha: 10,
    posicaoJogador: window.posicaoAtual || 1,
    jogadorElement: null,
    nomeElement: null,
    saldo: window.saldo || 0,
    emMovimento: false
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
    
    // Configura validação do formulário de adicionar recompensa
    const formAdicionar = document.getElementById('form-adicionar-recompensa');
    if (formAdicionar) {
        formAdicionar.addEventListener('submit', function(e) {
            const posicaoInput = document.getElementById('input-posicao');
            if (posicaoInput && parseInt(posicaoInput.value) === 1) {
                e.preventDefault();
                alert('A casa 1 não pode ter recompensa. Por favor, escolha outra casa.');
                posicaoInput.focus();
            }
        });
    }
});

// Inicializa os modais com a nova estrutura
function inicializarModais() {
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharTodosModais();
        }
    });

    // Botões de fechar modal
    document.querySelectorAll('.modal-close, [data-modal-close]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const modal = this.closest('.modal-overlay');
            if (modal) {
                fecharModalPorElemento(modal);
            }
        });
    });

    // Prevenir fechamento ao clicar fora apenas para modais específicos
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal-overlay')) {
            // Verifica se o modal permite fechar clicando fora
            const modal = e.target;
            if (!modal.classList.contains('no-close-on-outside')) {
                fecharModalPorElemento(modal);
            }
        }
    });

    // Prevenir fechamento ao clicar dentro do conteúdo do modal
    document.querySelectorAll('.modal-card, .modal-content').forEach(conteudo => {
        conteudo.addEventListener('click', function(e) {
            e.stopPropagation();
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
    
    // Atualiza o conteúdo do modal de informações da casa
    const modal = document.getElementById('modal-casa-info');
    if (modal) {
        const titulo = modal.querySelector('.info-casa-titulo');
        const numeroCasa = modal.querySelector('.info-casa-numero');
        const descricao = modal.querySelector('.info-casa-descricao');
        const icon = modal.querySelector('.casa-info-icon');
        const status = modal.querySelector('.casa-status');
        const btnEditar = modal.querySelector('#btnEditarRecompensa');
        const btnAdicionar = modal.querySelector('#btnAdicionarRecompensa');
        const btnExcluir = modal.querySelector('#btnExcluirRecompensa');
        
        if (titulo) titulo.textContent = recompensa ? recompensa.titulo : `Casa ${numero}`;
        if (numeroCasa) numeroCasa.textContent = `Posição: ${numero}`;
        if (icon) icon.textContent = recompensa ? '🎁' : '🏠';
        
        if (descricao) {
            descricao.textContent = recompensa ? 
                recompensa.descricao : 
                'Esta é uma casa comum do tabuleiro. Avance para descobrir recompensas!';
        }
        
        // Atualiza status da casa
        if (status) {
            if (recompensa) {
                status.innerHTML = '<div class="status-badge recompensa">🎁 Tem Recompensa</div>';
            } else if (numero === 1) {
                status.innerHTML = '<div class="status-badge inicio">🎯 Casa Inicial</div>';
            } else if (numero === config.totalCasas) {
                status.innerHTML = '<div class="status-badge final">🏁 Casa Final</div>';
            } else {
                status.innerHTML = '<div class="status-badge comum">🏠 Casa Comum</div>';
            }
        }
        
        // Mostra/oculta botões baseado na existência de recompensa e se é criador
        if (window.ehCriador) {
            if (recompensa) {
                btnEditar.style.display = 'block';
                btnExcluir.style.display = 'block';
                btnAdicionar.style.display = 'none';
                btnExcluir.dataset.recompensaId = recompensa.id_recompensa;
            } else if (numero !== 1) {
                btnAdicionar.style.display = 'block';
                btnEditar.style.display = 'none';
                btnExcluir.style.display = 'none';
            } else {
                btnAdicionar.style.display = 'none';
                btnEditar.style.display = 'none';
                btnExcluir.style.display = 'none';
            }
        } else {
            btnAdicionar.style.display = 'none';
            btnEditar.style.display = 'none';
            btnExcluir.style.display = 'none';
        }
    }
    
    abrirModal('casa-info');
}

// Funções para criador
function editarRecompensaCasa() {
    const numeroCasa = document.querySelector('.info-casa-numero')?.textContent.split(': ')[1];
    if (numeroCasa) {
        fecharModal('casa-info');
        abrirModal('editar');
    }
}

function adicionarRecompensaCasa() {
    const numeroCasa = document.querySelector('.info-casa-numero')?.textContent.split(': ')[1];
    if (numeroCasa) {
        // Preenche automaticamente o campo de posição no modal de adicionar
        const posicaoInput = document.getElementById('input-posicao');
        if (posicaoInput) {
            posicaoInput.value = numeroCasa;
        }
        
        fecharModal('casa-info');
        abrirModal('adicionar');
    }
}

function excluirRecompensaCasa() {
    const btnExcluir = document.querySelector('#btnExcluirRecompensa');
    const recompensaId = btnExcluir?.dataset.recompensaId;
    
    if (recompensaId) {
        confirmarExclusao(parseInt(recompensaId));
        fecharModal('casa-info');
    }
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
        if (recompensa.posicao === 1) return;
        
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
        
        const primeiroNome = usuario.nome ? usuario.nome.split(' ')[0] : 'Usuário';
        const posicao = usuario.posicao_atual !== null && usuario.posicao_atual !== undefined ? 
            usuario.posicao_atual : 0;
        
        usuarioItem.innerHTML = `
            <span class="usuario-nome">${primeiroNome}</span>
            <span class="usuario-posicao">Casa: ${posicao}</span>
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
        
        const dataConquista = recompensa.data_conquista ? 
            new Date(recompensa.data_conquista).toLocaleDateString('pt-BR') : 
            'Data não disponível';
        
        card.innerHTML = `
            <div class="recompensa-titulo">${recompensa.titulo}</div>
            <div class="recompensa-descricao">${recompensa.descricao}</div>
            <div class="recompensa-info">
                <span>Conquistada em: ${dataConquista}</span>
                <span>Casa: ${recompensa.posicao}</span>
            </div>
        `;
        gridRecompensas.appendChild(card);
    });
}

// Atualiza informações do jogador no painel lateral
function atualizarInfoJogador() {
    const nomeCompleto = window.nomeJogador;
    const primeiroNome = nomeCompleto.split(' ')[0];
    document.getElementById('nome-jogador-display').textContent = primeiroNome;
    document.getElementById('posicao-atual').textContent = config.posicaoJogador;
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

// Posiciona o jogador em uma casa específica
function posicionarJogador(novaPosicao) {
    if (config.jogadorElement) {
        config.jogadorElement.remove();
        config.nomeElement.remove();
    }
    
    config.posicaoJogador = novaPosicao;
    const casa = document.querySelector(`.casa[data-numero="${novaPosicao}"]`);
    
    if (casa) {
        casa.classList.add('visitada');
        casa.classList.add('recentemente');
        setTimeout(() => {
            casa.classList.remove('recentemente');
        }, 300);
        
        config.jogadorElement = document.createElement('div');
        config.jogadorElement.className = 'boneco';
        if (config.emMovimento) {
            config.jogadorElement.classList.add('movendo', 'jogador-movendo');
        }
        config.jogadorElement.textContent = '🧑‍💼';
        
        config.nomeElement = document.createElement('div');
        config.nomeElement.className = 'nome-jogador';
        const primeiroNome = window.nomeJogador.split(' ')[0];
        config.nomeElement.textContent = primeiroNome;
        
        casa.appendChild(config.jogadorElement);
        casa.appendChild(config.nomeElement);
        
        if (config.emMovimento) {
            setTimeout(() => {
                config.jogadorElement.classList.remove('movendo', 'jogador-movendo');
            }, 300);
        }
    }
    
    atualizarInfoJogador();
}

// Rola o dado e move o jogador
function rolarDado() {
    if (config.saldo <= 0 || config.emMovimento) return;
    
    const dado = document.getElementById('dado');
    const resultadoElem = document.getElementById('res-num');
    const btnGirar = document.getElementById('btnGirarDado');
    
    dado.classList.add('rolling');
    dado.textContent = '...';
    resultadoElem.textContent = '...';
    btnGirar.disabled = true;
    btnGirar.textContent = '🎲 Rolando...';
    
    fetch(`/tabuleiro/projeto/${window.idProjeto}/girar_dado`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dado.textContent = data.resultado_dado;
            resultadoElem.textContent = data.resultado_dado;
            dado.classList.remove('rolling');
            config.saldo = data.saldo_restante;
            atualizarSaldo();

            // NÃO converter para 0-based - usar posições 1-based diretamente
            const posInicial = config.posicaoJogador;
            const posFinal = data.nova_posicao; // JÁ É 1-based
            
            moverJogadorComAnimacao(posInicial, posFinal, data.resultado_dado);
            
            if (data.recompensa) {
                setTimeout(() => {
                    mostrarMensagemRecompensa(data.recompensa.titulo, data.recompensa.descricao);
                }, data.resultado_dado * 300 + 500);
            }
        } else {
            alert('Erro: ' + data.error);
            dado.textContent = '–';
            resultadoElem.textContent = '–';
            dado.classList.remove('rolling');
            btnGirar.disabled = false;
            btnGirar.textContent = '🎲 Girar Dado';
        }
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

// Move o jogador com animação passo a passo
function moverJogadorComAnimacao(posicaoInicial, posicaoFinal, passos) {
    if (config.emMovimento) return;
    
    config.emMovimento = true;
    let posicaoAtual = posicaoInicial;
    const btnGirar = document.getElementById('btnGirarDado');
    
    if (btnGirar) {
        btnGirar.disabled = true;
        btnGirar.textContent = '🚶 Movendo...';
    }
    
    const intervalo = setInterval(() => {
        posicaoAtual++;
        posicionarJogador(posicaoAtual);
        
        const casaAtual = document.querySelector(`.casa[data-numero="${posicaoAtual}"]`);
        if (casaAtual) {
            casaAtual.classList.add('casa-destacada');
            setTimeout(() => {
                casaAtual.classList.remove('casa-destacada');
            }, 200);
            criarEfeitoParticulas(casaAtual);
        }
        
        if (posicaoAtual >= posicaoFinal) {
            clearInterval(intervalo);
            config.emMovimento = false;
            config.posicaoJogador = posicaoFinal;
            
            if (btnGirar) {
                btnGirar.disabled = config.saldo <= 0;
                btnGirar.textContent = '🎲 Girar Dado';
            }
            
            const casaFinal = document.querySelector(`.casa[data-numero="${posicaoFinal + 1}"]`);
            if (casaFinal) {
                casaFinal.classList.add('casa-chegada');
                setTimeout(() => {
                    casaFinal.classList.remove('casa-chegada');
                }, 1000);
            }
            
            if (posicaoFinal + 1 === config.totalCasas) {
                setTimeout(() => {
                    mostrarMensagemVitoria("🎉 Parabéns! Você chegou ao final do tabuleiro!");
                    document.getElementById('btnRecomecar').style.display = 'block';
                }, 500);
            }
        }
    }, 300);
}

// Cria efeito de partículas ao passar pelas casas
function criarEfeitoParticulas(elemento) {
    const rect = elemento.getBoundingClientRect();
    const particulasContainer = document.createElement('div');
    particulasContainer.className = 'particulas-container';
    particulasContainer.style.position = 'fixed';
    particulasContainer.style.left = `${rect.left + rect.width / 2}px`;
    particulasContainer.style.top = `${rect.top + rect.height / 2}px`;
    particulasContainer.style.pointerEvents = 'none';
    particulasContainer.style.zIndex = '1000';
    
    document.body.appendChild(particulasContainer);
    
    for (let i = 0; i < 8; i++) {
        const particula = document.createElement('div');
        particula.className = 'particula';
        particula.style.position = 'absolute';
        particula.style.width = '6px';
        particula.style.height = '6px';
        particula.style.background = getCorParticula();
        particula.style.borderRadius = '50%';
        particula.style.opacity = '0.8';
        
        const angle = (i / 8) * Math.PI * 2;
        const distance = 20 + Math.random() * 30;
        const duration = 400 + Math.random() * 300;
        
        particula.style.animation = `voarParticula ${duration}ms ease-out forwards`;
        particula.style.setProperty('--angle', angle);
        particula.style.setProperty('--distance', distance);
        
        particulasContainer.appendChild(particula);
        
        setTimeout(() => {
            particula.remove();
        }, duration);
    }
    
    setTimeout(() => {
        particulasContainer.remove();
    }, 1000);
}

// Retorna cor aleatória para as partículas
function getCorParticula() {
    const cores = [
        'var(--azul-claro)',
        'var(--verde)',
        'var(--roxo)',
        'var(--dourado)',
        '#FF6B6B',
        '#4ECDC4',
        '#45B7D1',
        '#96CEB4'
    ];
    return cores[Math.floor(Math.random() * cores.length)];
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
    
    const modal = document.getElementById('modal-ganhou');
    if (modal) {
        const winTitle = modal.querySelector('.win-title');
        const winDesc = modal.querySelector('.win-desc');
        const winSaldo = modal.querySelector('.win-saldo');
        
        if (winTitle) winTitle.textContent = mensagemAleatoria;
        if (winDesc) winDesc.textContent = `Você ganhou: "${titulo}" - ${descricao}`;
        if (winSaldo) winSaldo.textContent = "Recompensa conquistada!";
    }
    
    abrirModal('ganhou');
}

// Mostra mensagem de vitória personalizada
function mostrarMensagemVitoria(mensagem) {
    const modal = document.getElementById('modal-ganhou');
    if (modal) {
        const winTitle = modal.querySelector('.win-title');
        const winDesc = modal.querySelector('.win-desc');
        const winSaldo = modal.querySelector('.win-saldo');
        
        if (winTitle) winTitle.textContent = mensagem;
        if (winDesc) winDesc.textContent = "Você completou todo o tabuleiro! Parabéns pela conquista!";
        if (winSaldo) winSaldo.textContent = "🎊 Missão Cumprida!";
    }
    
    abrirModal('ganhou');
}

// ================================
// FUNÇÕES DE MODAL ATUALIZADAS
// ================================

// Função para abrir modal
function abrirModal(tipo) {
    const modal = document.getElementById(`modal-${tipo}`);
    if (modal) {
        // Adiciona classe para modais que não fecham ao clicar fora
        if (tipo === 'adicionar' || tipo === 'editar') {
            modal.classList.add('no-close-on-outside');
        }
        
        modal.style.display = 'flex';
        modal.setAttribute('aria-modal', 'true');
        document.body.classList.add('modal-open');
        
        setTimeout(() => {
            const focusElement = modal.querySelector('button, input, textarea, select');
            if (focusElement) focusElement.focus();
        }, 100);
    }
}

// Função para fechar modal
function fecharModal(tipo) {
    const modal = document.getElementById(`modal-${tipo}`);
    if (modal) {
        modal.style.display = 'none';
        modal.setAttribute('aria-modal', 'false');
        modal.classList.remove('no-close-on-outside');
        document.body.classList.remove('modal-open');
    }
}

// Nova função para fechar modal por elemento
function fecharModalPorElemento(modalElement) {
    modalElement.style.display = 'none';
    modalElement.setAttribute('aria-modal', 'false');
    modalElement.classList.remove('no-close-on-outside');
    document.body.classList.remove('modal-open');
}

// Nova função para fechar todos os modais
function fecharTodosModais() {
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.style.display = 'none';
        modal.setAttribute('aria-modal', 'false');
        modal.classList.remove('no-close-on-outside');
    });
    document.body.classList.remove('modal-open');
}

// Confirmação de exclusão
// Confirmação de exclusão - CORRIGIDA
function confirmarExclusao(id) {
    const form = document.getElementById('form-excluir');
    if (form) {
        // Monta a URL corretamente para a rota Flask
        form.action = `/tabuleiro/projeto/${window.idProjeto}/excluir/${id}`;
        abrirModal('confirmacao');
    }
}

// Recomeçar jogo
function recomecar() {
    if (confirm('Tem certeza que deseja recomeçar o jogo? Sua posição será resetada para o início.')) {
        fetch(`/tabuleiro/projeto/${window.idProjeto}/recomecar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelectorAll('.casa.visitada').forEach(casa => {
                    casa.classList.remove('visitada');
                });
                
                if (config.jogadorElement) {
                    config.jogadorElement.remove();
                    config.nomeElement.remove();
                    config.jogadorElement = null;
                    config.nomeElement = null;
                }
                
                config.posicaoJogador = 0;
                config.saldo = data.novo_saldo;
                posicionarJogador(0);
                atualizarSaldo();
                document.getElementById('btnRecomecar').style.display = 'none';
                document.getElementById('dado').textContent = '–';
                document.getElementById('res-num').textContent = '–';
                carregarRecompensasGanhas();
                flash("Jogo recomeçado com sucesso!", "success");
            } else {
                alert('Erro ao recomeçar jogo: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao recomeçar jogo');
        });
    }
}

// Voltar para o projeto
function voltarParaProjeto() {
    window.location.href = `/projeto/${window.idProjeto}`;
}

// Função auxiliar para mostrar mensagens flash
function flash(mensagem, tipo) {
    alert(mensagem);
}

// Configurar modais com a nova estrutura
function configurarModais() {
    // Fechar modal ao clicar fora
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                const modalId = this.id.replace('modal-', '');
                fecharModal(modalId);
            }
        });
    });
    
    // Fechar modal com ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                const modalId = modal.id.replace('modal-', '');
                fecharModal(modalId);
            });
        }
    });
    
    // Botões de fechar
    document.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', function() {
            const modal = this.closest('.modal-overlay');
            const modalId = modal.id.replace('modal-', '');
            fecharModal(modalId);
        });
    });
}

// Inicializar modais quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    configurarModais();
});