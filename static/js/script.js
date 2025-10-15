
document.addEventListener('DOMContentLoaded', function() {
  configurarSubmenuSuave();
  configurarFormulariosSimples();
  // atualiza listas se houver (opcional)
  if (typeof renderEspacos === 'function') renderEspacos();
  if (typeof renderProjetos === 'function') renderProjetos();
});

//submenu abrir/fechar
function configurarSubmenuSuave() {
  var link = document.getElementById('workspaceLink');
  var submenu = document.getElementById('workspaceSubmenu');

  if (!link || !submenu) return; // se não existir nessa página, sai

  // Usa apenas maxHeight para animação — evita conflitos com display:none
  submenu.style.overflow = 'hidden';
  submenu.style.maxHeight = '0px';       // estado inicial: fechado
  submenu.style.transition = 'max-height 250ms ease';

  //ao clicar no link, alterna entre aberto/fechado
  link.addEventListener('click', function(e) {
    e.preventDefault();
    //se estiver fechado -> abrir
    if (submenu.style.maxHeight === '0px' || submenu.style.maxHeight === '') {
      submenu.style.maxHeight = submenu.scrollHeight + 'px';
    } else {
      // fechar
      submenu.style.maxHeight = '0px';
    }
  });
}

//config form 
function configurarFormulariosSimples() {
  //criar Espaço
  var formEspaco = document.getElementById('formEspaco');
  if (formEspaco) {
    formEspaco.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarEspacoSimples();
    });
    // botão cancelar dentro do form (procura data-cancel ou button[type="button"])
    var cancelEsp = formEspaco.querySelector('button[data-cancel="espaco"]') || formEspaco.querySelector('button[type="button"]');
    if (cancelEsp) cancelEsp.addEventListener('click', cancelarEspaco);
  }

  //criar Projeto
  var formProjeto = document.getElementById('formProjeto');
  if (formProjeto) {
    formProjeto.addEventListener('submit', function(e) {
      e.preventDefault();
      salvarProjetoSimples();
    });
    var cancelProj = formProjeto.querySelector('button[data-cancel="projeto"]') || formProjeto.querySelector('button[type="button"]');
    if (cancelProj) cancelProj.addEventListener('click', cancelarProjeto);
  }

  // editar Projeto
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

//função salvar
function salvarEspacoSimples() {
  var campo = document.getElementById('nomeEspaco');
  var nome = campo ? campo.value.trim() : '';

  if (nome === '') {
    alert('Por favor, digite o nome do espaço!');
    if (campo) campo.focus();
    return;
  }

  // salva no localStorage (opcional)
  var espacos = JSON.parse(localStorage.getItem('espacos') || '[]');
  espacos.push({ nome: nome, criadoEm: new Date().toISOString() });
  localStorage.setItem('espacos', JSON.stringify(espacos));

  alert('Criado com sucesso!');
  limparFormularioEspaco();
  // recolhe submenu (volta ao estado inicial)
  recolherSubmenu();
  if (typeof renderEspacos === 'function') renderEspacos();
}

function salvarProjetoSimples() {
  var nomeCampo = document.getElementById('nomeProjeto');
  var descCampo = document.getElementById('descricaoProjeto');

  var nome = nomeCampo ? nomeCampo.value.trim() : '';
  var desc = descCampo ? descCampo.value.trim() : '';

  if (nome === '') {
    alert('Por favor, digite o nome do projeto!');
    if (nomeCampo) nomeCampo.focus();
    return;
  }

  var projetos = JSON.parse(localStorage.getItem('projetos') || '[]');
  projetos.push({ nome: nome, desc: desc, progresso: 0, criadoEm: new Date().toISOString() });
  localStorage.setItem('projetos', JSON.stringify(projetos));

  alert('Criado com sucesso!');
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
      alert('Criado com sucesso!');
      limparFormularioEditar();
      localStorage.removeItem('editarIndex');
      if (typeof renderProjetos === 'function') renderProjetos();
      return;
    }
  }


  alert('Criado com sucesso!');
  limparFormularioEditar();
}

// função de limpar/cancelar
function cancelarEspaco() {
  limparFormularioEspaco();
  recolherSubmenu();
  alert('Operação cancelada!');
}

function cancelarProjeto() {
  limparFormularioProjeto();
  alert('Operação cancelada!');
}

function cancelarEditar() {
  limparFormularioEditar();
  alert('Operação cancelada!');
}

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

// recolher submenu
function recolherSubmenu() {
  var submenu = document.getElementById('workspaceSubmenu');
  if (!submenu) return;
  submenu.style.maxHeight = '0px';
}
