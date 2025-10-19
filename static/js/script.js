document.addEventListener('DOMContentLoaded', function() {
  configurarSubmenuSuave();
  configurarFormulariosSimples();
  // atualiza listas se houver (opcional)
  if (typeof renderEspacos === 'function') renderEspacos();
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
  // Criar Espaço
  var formEspaco = document.getElementById('formEspaco');
  if (formEspaco) {
    formEspaco.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarEspacoSimples();
    });
    var cancelEsp = formEspaco.querySelector('button[data-cancel="espaco"]') || formEspaco.querySelector('button[type="button"]');
    if (cancelEsp) cancelEsp.addEventListener('click', cancelarEspaco);
    
    document.querySelector('[data-cancel="espaco"]').addEventListener('click', function() {
      window.location.href = '/home';
    });
  }

  // Criar Projeto
  var formProjeto = document.getElementById('formProjeto');
  if (formProjeto) {
    formProjeto.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarProjetoSimples();
    });
    var cancelProj = formProjeto.querySelector('button[data-cancel="projeto"]') || formProjeto.querySelector('button[type="button"]');
    if (cancelProj) cancelProj.addEventListener('click', cancelarProjeto);
  }

  // Editar Projeto
  var formEditar = document.getElementById('formEditar');
  if (formEditar) {
    formEditar.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarEdicaoSimples();
    });
    var cancelEdit = formEditar.querySelector('button[data-cancel="editar"]') || formEditar.querySelector('button[type="button"]');
    if (cancelEdit) cancelEdit.addEventListener('click', cancelarEditar);
  }
}

// ========== FUNÇÕES DE SALVAR ==========
function salvarEspacoSimples() {
  var campo = document.getElementById('nomeEspaco');
  var nome = campo ? campo.value.trim() : '';

  if (nome === '') {
    mostrarMensagemTemporaria('Por favor, digite o nome do espaço!', 3000);
    if (campo) campo.focus();
    return;
  }

  var espacos = JSON.parse(localStorage.getItem('espacos') || '[]');
  espacos.push({ nome: nome, criadoEm: new Date().toISOString() });
  localStorage.setItem('espacos', JSON.stringify(espacos));

  mostrarMensagemTemporaria('Espaço criado com sucesso!');
  limparFormularioEspaco();
  recolherSubmenu();
  if (typeof renderEspacos === 'function') renderEspacos();
}

function salvarProjetoSimples() {
  var nomeCampo = document.getElementById('nomeProjeto');
  var descCampo = document.getElementById('descricaoProjeto');

  var nome = nomeCampo ? nomeCampo.value.trim() : '';
  var desc = descCampo ? descCampo.value.trim() : '';

  if (nome === '') {
    mostrarMensagemTemporaria('Por favor, digite o nome do projeto!', 3000);
    if (nomeCampo) nomeCampo.focus();
    return;
  }

  var projetos = JSON.parse(localStorage.getItem('projetos') || '[]');
  projetos.push({ nome: nome, desc: desc, progresso: 0, criadoEm: new Date().toISOString() });
  localStorage.setItem('projetos', JSON.stringify(projetos));

  mostrarMensagemTemporaria('Projeto criado com sucesso!');
  limparFormularioProjeto();
  if (typeof renderProjetos === 'function') renderProjetos();
}

function salvarEdicaoSimples() {
  var idx = Number(localStorage.getItem('editarIndex'));
  var nomeCampo = document.getElementById('editNomeProjeto');
  var descCampo = document.getElementById('editDescricaoProjeto');

  if (!isNaN(idx)) {
    var projetos = JSON.parse(localStorage.getItem('projetos') || '[]');
    if (projetos[idx]) {
      projetos[idx].nome = nomeCampo ? nomeCampo.value.trim() : projetos[idx].nome;
      projetos[idx].desc = descCampo ? descCampo.value.trim() : projetos[idx].desc;
      localStorage.setItem('projetos', JSON.stringify(projetos));
      mostrarMensagemTemporaria('Projeto editado com sucesso!');
      limparFormularioEditar();
      localStorage.removeItem('editarIndex');
      if (typeof renderProjetos === 'function') renderProjetos();
      return;
    }
  }

  mostrarMensagemTemporaria('Projeto salvo com sucesso!');
  limparFormularioEditar();
}

// ========== FUNÇÕES DE LIMPAR/CANCELAR ==========
function cancelarEspaco() {
  limparFormularioEspaco();
  recolherSubmenu();
  mostrarMensagemTemporaria('Operação cancelada!');
}

function cancelarProjeto() {
  limparFormularioProjeto();
  mostrarMensagemTemporaria('Operação cancelada!');
}

function cancelarEditar() {
  limparFormularioEditar();
  mostrarMensagemTemporaria('Operação cancelada!');
}

// ========== FUNÇÕES AUXILIARES ==========
function limparFormularioEspaco() {
  var campo = document.getElementById('nomeEspaco');
  if (campo) campo.value = '';
}

function limparFormularioProjeto() {
  var n = document.getElementById('nomeProjeto');
  var d = document.getElementById('descricaoProjeto');
  var a = document.getElementById('atribuidoProjeto');
  if (n) n.value = '';
  if (d) d.value = '';
  if (a) a.value = '';
}

function limparFormularioEditar() {
  var n = document.getElementById('editNomeProjeto');
  var d = document.getElementById('editDescricaoProjeto');
  var a = document.getElementById('editAtribuidoProjeto');
  if (n) n.value = '';
  if (d) d.value = '';
  if (a) a.value = '';
}

function recolherSubmenu() {
  var submenu = document.getElementById('workspaceSubmenu');
  if (!submenu) return;
  submenu.style.maxHeight = '0px';
}