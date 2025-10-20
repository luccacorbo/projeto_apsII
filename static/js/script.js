document.addEventListener('DOMContentLoaded', function() {
  configurarSubmenuSuave();
  configurarFormulariosSimples();
  verificarMensagemPersistente(); // Nova função
  // atualiza listas se houver (opcional)
  if (typeof renderProjetos === 'function') renderProjetos();
});

// ========== FUNÇÃO DE MENSAGEM TEMPORÁRIA ==========
function mostrarMensagemTemporaria(mensagem, tipo = 'sucesso', tempo = 3000) {
  const mensagemEl = document.createElement('div');
  mensagemEl.textContent = mensagem;
  
  // Define a cor baseada no tipo
  const corFundo = tipo === 'sucesso' ? '#4CAF50' : '#ae2f26ff';
  
  mensagemEl.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${corFundo};
      color: white;
      padding: 15px 20px;
      border-radius: 5px;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      font-family: Arial, sans-serif;
      transition: opacity 0.3s ease;
  `;
  
  document.body.appendChild(mensagemEl);
  
  setTimeout(() => {
      if (mensagemEl.parentNode) {
          mensagemEl.style.opacity = '0';
          setTimeout(() => {
              if (mensagemEl.parentNode) {
                  document.body.removeChild(mensagemEl);
              }
          }, 300);
      }
  }, tempo);
}

// ========== NOVA FUNÇÃO: MENSAGEM PERSISTENTE ==========
function mostrarMensagemPersistente(mensagem, tipo = 'sucesso') {
  // Salva a mensagem no localStorage
  localStorage.setItem('mensagemTemporaria', JSON.stringify({
    mensagem: mensagem,
    tipo: tipo,
    timestamp: new Date().getTime()
  }));
}

// ========== NOVA FUNÇÃO: VERIFICAR MENSAGEM PERSISTENTE ==========
function verificarMensagemPersistente() {
  const mensagemSalva = localStorage.getItem('mensagemTemporaria');
  
  if (mensagemSalva) {
    const { mensagem, tipo } = JSON.parse(mensagemSalva);
    
    // Remove do localStorage imediatamente
    localStorage.removeItem('mensagemTemporaria');
    
    // Mostra a mensagem após um pequeno delay para garantir que a página carregou
    setTimeout(() => {
      mostrarMensagemTemporaria(mensagem, tipo, 4000);
    }, 100);
  }
}

// ========== CONFIGURAÇÃO DO SUBMENU ==========
function configurarSubmenuSuave() {
  var link = document.getElementById('workspaceLink');
  var submenu = document.getElementById('workspaceSubmenu');

  if (!link || !submenu) return;

  submenu.style.overflow = 'hidden';
  submenu.style.maxHeight = '0px';
  submenu.style.transition = 'max-height 250ms ease';

  link.addEventListener('click', function(e) {
    e.preventDefault();
    if (submenu.style.maxHeight === '0px' || submenu.style.maxHeight === '') {
      submenu.style.maxHeight = submenu.scrollHeight + 'px';
    } else {
      submenu.style.maxHeight = '0px';
    }
  });
}

// ========== CONFIGURAÇÃO DOS FORMULÁRIOS ==========
function configurarFormulariosSimples() {
  // Criar Projeto
  var formProjeto = document.getElementById('formProjeto');
  if (formProjeto) {
    formProjeto.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarProjetoSimples();
    });
    var cancelProj = formProjeto.querySelector('button[data-cancel="projeto"]') || formProjeto.querySelector('button[type="button"]');
    if (cancelProj) cancelProj.addEventListener('click', cancelarProjeto);
    
    document.querySelector('[data-cancel="projeto"]').addEventListener('click', function() {
      // Usar mensagem persistente antes do redirecionamento
      mostrarMensagemPersistente('Operação cancelada!', 'sucesso');
      setTimeout(() => {
        window.location.href = '/home';
      }, 100);
    });
  }
}

// ========== FUNÇÕES DE SALVAR ==========
function salvarProjetoSimples() {
  var campo = document.getElementById('nomeProjeto');
  var nome = campo ? campo.value.trim() : null;

  if (nome === null) {
    mostrarMensagemTemporaria('Por favor, digite o nome do projeto!', 'erro', 3000);
    if (campo) campo.focus();
    return;
  }

  var projetos = JSON.parse(localStorage.getItem('projetos') || '[]');
  projetos.push({ nome: nome, criadoEm: new Date().toISOString() });
  localStorage.setItem('projetos', JSON.stringify(projetos));

  // Usar mensagem persistente para redirecionamentos
  mostrarMensagemPersistente('Projeto criado com sucesso!', 'sucesso');
  
  limparFormularioProjeto();
  recolherSubmenu();
  
  // Redirecionar após um pequeno delay
  setTimeout(() => {
    if (typeof renderProjetos === 'function') {
      renderProjetos();
    } else {
      // Se não houver função renderProjetos, redireciona para home
      window.location.href = '/home';
    }
  }, 100);
}

// ========== FUNÇÕES DE LIMPAR/CANCELAR ==========
function cancelarProjeto() {
  limparFormularioProjeto();
  recolherSubmenu();
  mostrarMensagemTemporaria('Operação cancelada!', 'sucesso');
}

// ========== FUNÇÕES AUXILIARES ==========
function limparFormularioProjeto() {
  var campo = document.getElementById('nomeProjeto');
  if (campo) campo.value = '';
}

// ========== FUNÇÕES PARA MENSAGENS DE LOGIN/CADASTRO ==========

// Função para mostrar mensagem de login bem-sucedido
function mostrarMensagemLoginSucesso(nomeUsuario) {
    mostrarMensagemPersistente(`Bem-vindo(a), ${nomeUsuario}!`, 'sucesso');
}

// Função para mostrar mensagem de erro de login
function mostrarMensagemErroLogin() {
    mostrarMensagemTemporaria('Email ou senha incorretos!', 'erro', 4000);
}

// Função para mostrar mensagem de cadastro bem-sucedido
function mostrarMensagemCadastroSucesso() {
    mostrarMensagemPersistente('Cadastro realizado com sucesso! Faça login para continuar.', 'sucesso');
}

// Função para mostrar mensagem de erro de cadastro
function mostrarMensagemErroCadastro(mensagem) {
    mostrarMensagemTemporaria(mensagem || 'Erro ao realizar cadastro!', 'erro', 4000);
}

// Função para mostrar mensagem de logout
function mostrarMensagemLogout() {
    mostrarMensagemPersistente('Logout realizado com sucesso!', 'sucesso');
}

// Função para mostrar mensagem de sessão expirada
function mostrarMensagemSessaoExpirada() {
    mostrarMensagemTemporaria('Sua sessão expirou. Faça login novamente.', 'erro', 5000);
}

// Função para mostrar mensagem de acesso negado
function mostrarMensagemAcessoNegado() {
    mostrarMensagemTemporaria('Acesso negado. Faça login para continuar.', 'erro', 4000);
}

// Função para verificar e mostrar mensagens específicas da página
function verificarMensagensEspecificas() {
    // Verificar se há parâmetros de URL indicando mensagens
    const urlParams = new URLSearchParams(window.location.search);
    
    // Mensagem de logout
    if (urlParams.get('logout') === 'success') {
        mostrarMensagemLogout();
        // Limpar parâmetro da URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Mensagem de cadastro bem-sucedido
    if (urlParams.get('cadastro') === 'success') {
        mostrarMensagemCadastroSucesso();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
    
    // Mensagem de sessão expirada
    if (urlParams.get('sessao') === 'expirada') {
        mostrarMensagemSessaoExpirada();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// ========== DETECÇÃO AUTOMÁTICA DE MENSAGENS DO SERVIDOR ==========

// Função para detectar mensagens de erro nos formulários
function configurarMensagensFormularioLogin() {
    const formLogin = document.querySelector('form[action*="login"]');
    const formCadastro = document.querySelector('form[action*="cadastro"]');
    
    if (formLogin) {
        // Verificar se há mensagem de erro do servidor no formulário de login
        const alertaErro = formLogin.querySelector('.alert-error, .error-message, [class*="error"]');
        if (alertaErro && alertaErro.textContent.trim()) {
            setTimeout(() => {
                mostrarMensagemErroLogin();
            }, 500);
        }
    }
    
    if (formCadastro) {
        // Verificar se há mensagem de erro do servidor no formulário de cadastro
        const alertaErro = formCadastro.querySelector('.alert-error, .error-message, [class*="error"]');
        if (alertaErro && alertaErro.textContent.trim()) {
            setTimeout(() => {
                mostrarMensagemErroCadastro(alertaErro.textContent.trim());
            }, 500);
        }
        
        // Verificar se há mensagem de sucesso
        const alertaSucesso = formCadastro.querySelector('.alert-success, .success-message, [class*="success"]');
        if (alertaSucesso && alertaSucesso.textContent.trim()) {
            setTimeout(() => {
                mostrarMensagemCadastroSucesso();
            }, 500);
        }
    }
}

// ========== INTEGRAÇÃO COM O SISTEMA EXISTENTE ==========

// Atualizar a função DOMContentLoaded para incluir as novas verificações
document.addEventListener('DOMContentLoaded', function() {
    configurarSubmenuSuave();
    configurarFormulariosSimples();
    verificarMensagemPersistente();
    verificarMensagensEspecificas();
    configurarMensagensFormularioLogin();
    
    // atualiza listas se houver (opcional)
    if (typeof renderProjetos === 'function') renderProjetos();
    
    // Verificar se o usuário está logado e mostrar mensagem de boas-vindas
    verificarUsuarioLogado();
});

// Função para verificar se o usuário acabou de fazer login
function verificarUsuarioLogado() {
    // Verificar se há indicação de login recente no sessionStorage
    const loginRecente = sessionStorage.getItem('loginRecente');
    
    if (loginRecente) {
        const nomeUsuario = sessionStorage.getItem('usuarioNome');
        if (nomeUsuario) {
            setTimeout(() => {
                mostrarMensagemLoginSucesso(nomeUsuario);
            }, 1000);
        }
        
        // Limpar a flag de login recente
        sessionStorage.removeItem('loginRecente');
        sessionStorage.removeItem('usuarioNome');
    }
}

// ========== INTEGRAÇÃO COM O BACKEND ==========

// Função para ser chamada após login bem-sucedido no backend
function onLoginSucesso(nomeUsuario) {
    sessionStorage.setItem('loginRecente', 'true');
    sessionStorage.setItem('usuarioNome', nomeUsuario);
}

// Função para ser chamada após cadastro bem-sucedido no backend
function onCadastroSucesso() {
    // Redirecionar para login com parâmetro de sucesso
    window.location.href = '/auth/login?cadastro=success';
}

// Função para ser chamada após logout
function onLogout() {
    sessionStorage.clear();
    localStorage.removeItem('mensagemTemporaria');
    window.location.href = '/auth/login?logout=success';
}

// ========== INTERCEPTAÇÃO DE LINKS DE LOGOUT ==========

// Configurar interceptação de clicks em links de logout
document.addEventListener('click', function(e) {
    const target = e.target.closest('a[href*="logout"], [onclick*="logout"]');
    
    if (target) {
        e.preventDefault();
        
        // Mostrar mensagem de confirmação
        if (confirm('Deseja realmente sair?')) {
            onLogout();
        }
    }
});

// ========== DETECÇÃO DE ERROS DE AUTENTICAÇÃO ==========

// Interceptar requisições AJAX para detectar erros de autenticação
(function() {
    const originalFetch = window.fetch;
    
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            if (response.status === 401) {
                // Não autorizado - sessão expirada
                mostrarMensagemSessaoExpirada();
                setTimeout(() => {
                    window.location.href = '/auth/login?sessao=expirada';
                }, 2000);
            }
            return response;
        });
    };
})();
