// Variáveis globais
let editMode = false;
let originalData = {};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    carregarDadosUsuario();
    carregarEstatisticas();
    inicializarEventListeners();
});

// Carregar dados do usuário
async function carregarDadosUsuario() {
    try {
        const response = await fetch('/api/perfil');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar dados do usuário');
        }
        
        const usuario = await response.json();
        preencherDadosUsuario(usuario);
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro ao carregar dados do perfil', 'error');
    }
}

// Preencher dados do usuário no formulário
function preencherDadosUsuario(usuario) {
    document.getElementById('user-nome').value = usuario.nome || '';
    document.getElementById('user-email').value = usuario.email || '';
    
    // Salvar dados originais
    originalData = {
        nome: usuario.nome || '',
        email: usuario.email || ''
    };
    
    // Atualizar inicial do profile pic
    const profilePic = document.getElementById('profile-pic');
    if (usuario.nome) {
        profilePic.textContent = usuario.nome.charAt(0).toUpperCase();
    }
}

// Carregar estatísticas do usuário
async function carregarEstatisticas() {
    try {
        const response = await fetch('/api/perfil/estatisticas');
        
        if (response.ok) {
            const estatisticas = await response.json();
            atualizarEstatisticas(estatisticas);
        }
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Atualizar estatísticas na interface
function atualizarEstatisticas(estatisticas) {
    document.getElementById('total-tarefas').textContent = estatisticas.total_tarefas || 0;
    document.getElementById('tarefas-pendentes').textContent = estatisticas.tarefas_pendentes || 0;
    document.getElementById('tarefas-concluidas').textContent = estatisticas.tarefas_concluidas || 0;
    document.getElementById('dias-ativo').textContent = estatisticas.dias_ativo || 0;
}

// Inicializar event listeners
function inicializarEventListeners() {
    const form = document.getElementById('profile-form');
    form.addEventListener('submit', salvarAlteracoes);
    
    // Validação de senha em tempo real
    const senhaInput = document.getElementById('user-senha');
    const confirmarSenhaInput = document.getElementById('user-confirmar-senha');
    
    senhaInput.addEventListener('input', validarForcaSenha);
    senhaInput.addEventListener('input', validarConfirmacaoSenha);
    confirmarSenhaInput.addEventListener('input', validarConfirmacaoSenha);
}

// Alternar modo de edição
function toggleEditMode() {
    editMode = !editMode;
    const inputs = document.querySelectorAll('.form-input');
    const editBtn = document.getElementById('edit-btn');
    const formActions = document.getElementById('form-actions');
    
    if (editMode) {
        // Entrar no modo edição
        inputs.forEach(input => {
            input.readOnly = false;
            input.classList.add('editable');
        });
        
        editBtn.innerHTML = '<span>❌</span> Cancelar';
        formActions.style.display = 'flex';
        
    } else {
        // Sair do modo edição
        cancelEdit();
    }
}

// Cancelar edição
function cancelEdit() {
    editMode = false;
    const inputs = document.querySelectorAll('.form-input');
    const editBtn = document.getElementById('edit-btn');
    const formActions = document.getElementById('form-actions');
    
    // Restaurar valores originais
    document.getElementById('user-nome').value = originalData.nome;
    document.getElementById('user-email').value = originalData.email;
    document.getElementById('user-senha').value = '';
    document.getElementById('user-confirmar-senha').value = '';
    
    // Restaurar estado dos inputs
    inputs.forEach(input => {
        input.readOnly = true;
        input.classList.remove('editable');
    });
    
    // Limpar mensagens de erro
    limparErros();
    
    // Restaurar botão e ações
    editBtn.innerHTML = '<span>✏️</span> Editar';
    formActions.style.display = 'none';
}

// Validar força da senha
function validarForcaSenha() {
    const senha = document.getElementById('user-senha').value;
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text');
    
    if (!senha) {
        strengthBar.className = 'strength-bar';
        strengthText.textContent = 'Força da senha';
        return;
    }
    
    let strength = 0;
    
    // Critérios de força
    if (senha.length >= 8) strength++;
    if (senha.match(/[a-z]/) && senha.match(/[A-Z]/)) strength++;
    if (senha.match(/\d/)) strength++;
    if (senha.match(/[^a-zA-Z\d]/)) strength++;
    
    // Atualizar visual
    if (strength <= 1) {
        strengthBar.className = 'strength-bar weak';
        strengthText.textContent = 'Senha fraca';
    } else if (strength <= 3) {
        strengthBar.className = 'strength-bar medium';
        strengthText.textContent = 'Senha média';
    } else {
        strengthBar.className = 'strength-bar strong';
        strengthText.textContent = 'Senha forte';
    }
}

// Validar confirmação de senha
function validarConfirmacaoSenha() {
    const senha = document.getElementById('user-senha').value;
    const confirmarSenha = document.getElementById('user-confirmar-senha').value;
    const errorElement = document.getElementById('confirmar-senha-error');
    
    if (confirmarSenha && senha !== confirmarSenha) {
        errorElement.textContent = 'As senhas não coincidem';
        return false;
    } else {
        errorElement.textContent = '';
        return true;
    }
}

// Validar formulário
function validarFormulario() {
    let valido = true;
    const nome = document.getElementById('user-nome').value.trim();
    const email = document.getElementById('user-email').value.trim();
    const senha = document.getElementById('user-senha').value;
    const confirmarSenha = document.getElementById('user-confirmar-senha').value;
    
    // Limpar erros anteriores
    limparErros();
    
    // Validar nome
    if (!nome) {
        document.getElementById('nome-error').textContent = 'Nome é obrigatório';
        valido = false;
    }
    
    // Validar email
    if (!email) {
        document.getElementById('email-error').textContent = 'E-mail é obrigatório';
        valido = false;
    } else if (!validarEmail(email)) {
        document.getElementById('email-error').textContent = 'E-mail inválido';
        valido = false;
    }
    
    // Validar senha se for preenchida
    if (senha) {
        if (senha.length < 6) {
            document.getElementById('senha-error').textContent = 'A senha deve ter pelo menos 6 caracteres';
            valido = false;
        }
        
        if (!validarConfirmacaoSenha()) {
            valido = false;
        }
    }
    
    return valido;
}

// Validar formato de email
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Limpar mensagens de erro
function limparErros() {
    const errorElements = document.querySelectorAll('.error-message');
    errorElements.forEach(element => {
        element.textContent = '';
    });
}

// Salvar alterações
async function salvarAlteracoes(event) {
    event.preventDefault();
    
    if (!validarFormulario()) {
        return;
    }
    
    const loadingSpinner = document.getElementById('loading-spinner');
    const submitBtn = event.target.querySelector('button[type="submit"]');
    
    try {
        // Mostrar loading
        loadingSpinner.style.display = 'inline-block';
        submitBtn.disabled = true;
        
        const formData = {
            nome: document.getElementById('user-nome').value.trim(),
            email: document.getElementById('user-email').value.trim(),
            senha: document.getElementById('user-senha').value || null
        };
        
        const response = await fetch('/api/perfil', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Erro ao atualizar perfil');
        }
        
        const resultado = await response.json();
        
        // Atualizar dados na sessão (se necessário)
        if (resultado.usuario) {
            originalData.nome = resultado.usuario.nome;
            originalData.email = resultado.usuario.email;
            
            // Atualizar profile pic
            const profilePic = document.getElementById('profile-pic');
            profilePic.textContent = resultado.usuario.nome.charAt(0).toUpperCase();
        }
        
        // Mostrar confirmação
        mostrarModalConfirmacao();
        
        // Sair do modo edição
        cancelEdit();
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao(error.message, 'error');
    } finally {
        // Esconder loading
        loadingSpinner.style.display = 'none';
        submitBtn.disabled = false;
    }
}

// Mostrar modal de confirmação
function mostrarModalConfirmacao() {
    document.getElementById('confirmation-modal').style.display = 'block';
}

// Fechar modal de confirmação
function closeConfirmationModal() {
    document.getElementById('confirmation-modal').style.display = 'none';
}

// Mostrar notificação
function mostrarNotificacao(mensagem, tipo) {
    // Remove notificação anterior se existir
    const notificacaoAnterior = document.querySelector('.notification');
    if (notificacaoAnterior) {
        notificacaoAnterior.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification ${tipo}`;
    notification.textContent = mensagem;
    
    document.body.appendChild(notification);
    
    // Remover após 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('confirmation-modal');
    if (event.target === modal) {
        closeConfirmationModal();
    }
}

function toggleSubmenu(event) {
  event.preventDefault();
  
  var submenu = document.getElementById('workspaceSubmenu');
  if (!submenu) return;
  
  // Alterna entre none e block
  if (submenu.style.display === 'block') {
    submenu.style.display = 'none';
  } else {
    submenu.style.display = 'block';
  }
}

// Fechar ao clicar fora
document.addEventListener('click', function(event) {
  var submenu = document.getElementById('workspaceSubmenu');
  var menuLink = document.querySelector('[onclick*="toggleSubmenu"]');
  
  if (submenu && !menuLink.contains(event.target) && !submenu.contains(event.target)) {
    submenu.style.display = 'none';
  }
});