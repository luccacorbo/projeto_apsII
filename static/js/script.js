document.addEventListener('DOMContentLoaded', function() {
  verificarMensagemPersistente();
  verificarMensagensEspecificas();
  configurarValidacaoClientSide(); // Mudei o nome da função
  verificarMensagensServidor(); // Nova função para mensagens do Flask
  configurarInterceptacaoLogout();
});

// ========== FUNÇÃO DE MENSAGEM TEMPORÁRIA ==========
function mostrarMensagemTemporaria(mensagem, tipo = 'sucesso', tempo = 3000) {
  const mensagemEl = document.createElement('div');
  mensagemEl.textContent = mensagem;
  
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

// ========== CONFIGURAÇÃO DE VALIDAÇÃO CLIENT-SIDE (CORRIGIDA) ==========
function configurarValidacaoClientSide() {
  const formLogin = document.querySelector('form[action*="login"]');
  const formCadastro = document.querySelector('form[action*="cadastro"]');
  
  // Configurar formulário de LOGIN - SEM preventDefault
  if (formLogin) {
    formLogin.addEventListener('submit', function(e) {
      const email = formLogin.querySelector('input[type="email"]');
      const senha = formLogin.querySelector('input[type="password"]');
      
      // Validação básica client-side
      if (!email.value.trim() || !senha.value.trim()) {
        e.preventDefault(); // Só impede se tiver erro
        mostrarMensagemTemporaria('Preencha todos os campos!', 'erro', 3000);
        return;
      }
      
      // Se passou na validação, permite o submit normal do formulário
      mostrarMensagemTemporaria('Entrando...', 'sucesso', 1000);
    });
  }
  
  // Configurar formulário de CADASTRO - SEM preventDefault
  if (formCadastro) {
    formCadastro.addEventListener('submit', function(e) {
      const nome = formCadastro.querySelector('input[name="nome"]');
      const email = formCadastro.querySelector('input[type="email"]');
      const senha = formCadastro.querySelector('input[name="senha"]');
      const confirmarSenha = formCadastro.querySelector('input[name="confirmar"]');
      
      // Validações client-side
      if (!nome.value.trim() || !email.value.trim() || !senha.value.trim() || !confirmarSenha.value.trim()) {
        e.preventDefault(); // Só impede se tiver erro
        mostrarMensagemTemporaria('Preencha todos os campos!', 'erro', 3000);
        return;
      }
      
      if (senha.value !== confirmarSenha.value) {
        e.preventDefault(); // Só impede se tiver erro
        mostrarMensagemTemporaria('As senhas não coincidem!', 'erro', 3000);
        return;
      }
      
      if (senha.value.length < 6) {
        e.preventDefault(); // Só impede se tiver erro
        mostrarMensagemTemporaria('A senha deve ter pelo menos 6 caracteres!', 'erro', 3000);
        return;
      }
      
      // Se passou na validação, permite o submit normal do formulário
      mostrarMensagemTemporaria('Criando sua conta...', 'sucesso', 1000);
    });
  }
}

// ========== DETECTAR MENSAGENS DO SERVIDOR (FLASK) ==========
function verificarMensagensServidor() {
  // Verificar se há elementos de erro do Flask
  const errorElement = document.querySelector('.error, .alert-danger, [class*="error"]');
  
  if (errorElement && errorElement.textContent.trim()) {
    const mensagem = errorElement.textContent.trim();
    
    // Mostrar como mensagem temporária também
    setTimeout(() => {
      mostrarMensagemTemporaria(mensagem, 'erro', 4000);
    }, 500);
  }
}

// ========== VERIFICAÇÃO DE MENSAGENS ESPECÍFICAS ==========
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
}

// ========== VERIFICAÇÃO DE USUÁRIO LOGADO ==========
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

// ========== INTERCEPTAÇÃO DE LINKS DE LOGOUT ==========
function configurarInterceptacaoLogout() {
  document.addEventListener('click', function(e) {
    const target = e.target.closest('a[href*="logout"]');
    
    if (target) {
      e.preventDefault();
      
      if (confirm('Deseja realmente sair?')) {
        // Mostrar mensagem antes de redirecionar
        mostrarMensagemTemporaria('Saindo...', 'sucesso', 1000);
        
        // Redirecionar após um breve delay
        setTimeout(() => {
          window.location.href = target.href;
        }, 800);
      }
    }
  });
}

// ========== REMOVA AS FUNÇÕES DE FETCH (não são mais necessárias) ==========
// Delete as funções enviarLogin() e enviarCadastro() completamente