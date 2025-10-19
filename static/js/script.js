document.addEventListener('DOMContentLoaded', function() {
  configurarSubmenuSuave();
  configurarFormulariosSimples();
  // atualiza listas se houver (opcional)
  if (typeof renderProjetos === 'function') renderProjetos();
});

// ========== FUNÇÃO DE MENSAGEM TEMPORÁRIA ==========
function mostrarMensagemTemporaria(mensagem, tempo = 2000) {
  const mensagemEl = document.createElement('div');
  mensagemEl.textContent = mensagem;
  mensagemEl.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #4CAF50;
      color: white;
      padding: 15px 20px;
      border-radius: 5px;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      font-family: Arial, sans-serif;
  `;
  
  document.body.appendChild(mensagemEl);
  
  setTimeout(() => {
      if (mensagemEl.parentNode) {
          document.body.removeChild(mensagemEl);
      }
  }, tempo);
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
      window.location.href = '/home';
    });
  }
}

// ========== FUNÇÕES DE SALVAR ==========
function salvarProjetoSimples() {
  var campo = document.getElementById('nomeProjeto');
  var nome = campo ? campo.value.trim() : '';

  if (nome === '') {
    mostrarMensagemTemporaria('Por favor, digite o nome do projeto!', 3000);
    if (campo) campo.focus();
    return;
  }

  var projetos = JSON.parse(localStorage.getItem('projetos') || '[]');
  projetos.push({ nome: nome, criadoEm: new Date().toISOString() });
  localStorage.setItem('projetos', JSON.stringify(projetos));

  mostrarMensagemTemporaria('Projeto criado com sucesso!');
  limparFormularioProjeto();
  recolherSubmenu();
  if (typeof renderProjetos === 'function') renderProjetos();
}

// ========== FUNÇÕES DE LIMPAR/CANCELAR ==========
function cancelarProjeto() {
  limparFormularioProjeto();
  recolherSubmenu();
  mostrarMensagemTemporaria('Operação cancelada!');
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
