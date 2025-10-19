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

function recolherSubmenu() {
  var submenu = document.getElementById('workspaceSubmenu');
  if (!submenu) return;
  submenu.style.maxHeight = '0px';
}