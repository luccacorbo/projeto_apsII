document.addEventListener('DOMContentLoaded', function() {
    verificarMensagemPersistente();
    verificarMensagensEspecificas();
    verificarMensagensSucesso(); 
    configurarValidacaoClientSide();
    verificarMensagensServidor(); 
    configurarInterceptacaoLogout(); // <-- FUNÇÃO ATUALIZADA
});

// ========== FUNÇÃO DE MENSAGEM TEMPORÁRIA ==========
function mostrarMensagemTemporaria(mensagem, tipo = 'sucesso', tempo = 3000) {
    const mensagemEl = document.createElement('div');
    mensagemEl.textContent = mensagem;
    
    // MUDANÇA: Usando o estilo do home.css
    mensagemEl.className = `flash-message ${tipo}`;
    
    document.body.appendChild(mensagemEl);

    // Animação de entrada
    setTimeout(() => {
        mensagemEl.classList.add('visible');
    }, 10);

    // Animação de saída
    setTimeout(() => {
        if (mensagemEl.parentNode) {
            mensagemEl.classList.remove('visible');
            setTimeout(() => {
                if (mensagemEl.parentNode) {
                    document.body.removeChild(mensagemEl);
                }
            }, 500);
        }
    }, tempo);
}

// ========== MENSAGEM PERSISTENTE ==========
function mostrarMensagemPersistente(mensagem, tipo = 'sucesso') {
    localStorage.setItem('mensagemTemporaria', JSON.stringify({
        mensagem: mensagem,
        tipo: tipo,
        timestamp: new Date().getTime()
    }));
}

function verificarMensagemPersistente() {
    const mensagemSalva = localStorage.getItem('mensagemTemporaria');
    
    if (mensagemSalva) {
        const { mensagem, tipo } = JSON.parse(mensagemSalva);
        localStorage.removeItem('mensagemTemporaria');
        
        setTimeout(() => {
            mostrarMensagemTemporaria(mensagem, tipo, 4000);
        }, 100);
    }
}

// ========== CONFIGURAÇÃO DE VALIDAÇÃO CLIENT-SIDE (Mantida) ==========
function configurarValidacaoClientSide() {
    // ... (código de validação mantido) ...
    const formLogin = document.querySelector('form[action*="login"]');
    const formCadastro = document.querySelector('form[action*="cadastro"]');
    const formRedefinir = document.querySelector('form[action*="redefinir-senha"]');
    
    if (formLogin) {
        formLogin.addEventListener('submit', function(e) {
            const email = formLogin.querySelector('input[type="email"]');
            const senha = formLogin.querySelector('input[type="password"]');
            
            if (!email.value.trim() || !senha.value.trim()) {
                e.preventDefault(); 
                mostrarMensagemTemporaria('Preencha todos os campos!', 'erro', 3000);
                return;
            }
            
            mostrarMensagemTemporaria('Entrando...', 'sucesso', 1000);
        });
    }
    
    if (formCadastro) {
        formCadastro.addEventListener('submit', function(e) {
            const nome = formCadastro.querySelector('input[name="nome"]');
            const email = formCadastro.querySelector('input[type="email"]');
            const senha = formCadastro.querySelector('input[name="senha"]');
            const confirmarSenha = formCadastro.querySelector('input[name="confirmar"]');
            
            if (!nome.value.trim() || !email.value.trim() || !senha.value.trim() || !confirmarSenha.value.trim()) {
                e.preventDefault(); 
                mostrarMensagemTemporaria('Preencha todos os campos!', 'erro', 3000);
                return;
            }
            
            if (senha.value !== confirmarSenha.value) {
                e.preventDefault(); 
                mostrarMensagemTemporaria('As senhas não coincidem!', 'erro', 3000);
                return;
            }
            
            if (senha.value.length < 6) {
                e.preventDefault(); 
                mostrarMensagemTemporaria('A senha deve ter pelo menos 6 caracteres!', 'erro', 3000);
                return;
            }
            
            mostrarMensagemTemporaria('Criando sua conta...', 'sucesso', 1000);
        });
    }

    if (formRedefinir) {
        formRedefinir.addEventListener('submit', function(e) {
            const novaSenha = formRedefinir.querySelector('input[name="nova_senha"]');
            const confirmarSenha = formRedefinir.querySelector('input[name="confirmar_senha"]');
            
            if (novaSenha.value !== confirmarSenha.value) {
                e.preventDefault();
                mostrarMensagemTemporaria('As senhas não coincidem!', 'erro', 3000);
                return;
            }

            if (novaSenha.value.length < 6) {
                e.preventDefault();
                mostrarMensagemTemporaria('A senha deve ter pelo menos 6 caracteres!', 'erro', 3000);
                return;
            }
            
            mostrarMensagemTemporaria('Redefinindo sua senha...', 'sucesso', 1000);
        });
    }
}

// ========== DETECTAR MENSAGENS DO SERVIDOR (Mantida) ==========
function verificarMensagensServidor() {
    const errorElement = document.querySelector('.error-message, .alert-danger, [class*="error"]');
    
    if (errorElement && errorElement.textContent.trim()) {
        const mensagem = errorElement.textContent.trim();
        setTimeout(() => {
            mostrarMensagemTemporaria(mensagem, 'erro', 4000);
        }, 500);
    }

    const successElement = document.querySelector('.success-message');
    
    if (successElement && successElement.textContent.trim()) {
        const mensagem = successElement.textContent.trim();
        if (!new URLSearchParams(window.location.search).get('success')) {
            setTimeout(() => {
                mostrarMensagemTemporaria(mensagem, 'sucesso', 4000);
            }, 500);
        }
    }
}

// ========== DETECTAR MENSAGENS DE SUCESSO DO SERVIDOR VIA URL (Mantida) ==========
function verificarMensagensSucesso() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('success')) {
        const mensagem = urlParams.get('success');
        mostrarMensagemTemporaria(mensagem, 'sucesso', 5000);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ========== VERIFICAÇÃO DE MENSAGENS ESPECÍFICAS (Mantida) ==========
function verificarMensagensEspecificas() {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('logout') === 'success') {
        mostrarMensagemTemporaria('Logout realizado com sucesso!', 'sucesso', 3000);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (urlParams.get('cadastro') === 'success') {
        mostrarMensagemTemporaria('Cadastro realizado com sucesso! Faça login para continuar.', 'sucesso', 4000);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (urlParams.get('sessao') === 'expirada') {
        mostrarMensagemTemporaria('Sua sessão expirou. Faça login novamente.', 'erro', 5000);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    if (urlParams.get('error')) {
        const mensagem = urlParams.get('error');
        mostrarMensagemTemporaria(mensagem, 'erro', 5000);
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ========== VERIFICAÇÃO DE USUÁRIO LOGADO (Mantida) ==========
function verificarUsuarioLogado() {
    const loginRecente = sessionStorage.getItem('loginRecente');
    
    if (loginRecente) {
        const nomeUsuario = sessionStorage.getItem('usuarioNome');
        if (nomeUsuario) {
            setTimeout(() => {
                mostrarMensagemTemporaria(`Bem-vindo(a), ${nomeUsuario}!`, 'sucesso', 3000);
            }, 500);
        }
        
        sessionStorage.removeItem('loginRecente');
        sessionStorage.removeItem('usuarioNome');
    }
}

// ========== MUDANÇA: INTERCEPTAÇÃO DE LOGOUT (AGORA USA O MODAL GLOBAL) ==========
function configurarInterceptacaoLogout() {
    // MUDANÇA: Aponta para o modal global
    const modal = document.getElementById('logout-modal'); 
    const cancelBtn = document.getElementById('logout-cancel-btn');
    const confirmBtn = document.getElementById('logout-confirm-btn'); 
    
    if (!modal || !cancelBtn || !confirmBtn) {
        console.log('Modal de logout não encontrado no DOM.');
        return;
    }

    // 1. Ouvir cliques em QUALQUER link de logout
    document.addEventListener('click', function(e) {
        const target = e.target.closest('a[href*="logout"]');
        
        // Se for um link de logout (E NÃO for o botão de confirmação)
        if (target && target.id !== 'logout-confirm-btn') {
            e.preventDefault();
            confirmBtn.href = target.href; 
            
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('visible'), 10);
        }
    });

    // 2. Fechar o modal ao clicar em "Cancelar"
    cancelBtn.addEventListener('click', function() {
        modal.classList.remove('visible');
        setTimeout(() => modal.style.display = 'none', 300);
    });

    // 3. Fechar o modal ao clicar fora dele (no overlay)
    modal.addEventListener('click', function(e) {
        if (e.target === modal) { 
            modal.classList.remove('visible');
            setTimeout(() => modal.style.display = 'none', 300);
        }
    });

    // 4. Lógica do botão de confirmação
    confirmBtn.addEventListener('click', function() {
        mostrarMensagemTemporaria('Saindo...', 'sucesso', 1000);
        modal.classList.remove('visible');
        setTimeout(() => modal.style.display = 'none', 300);
    });
}