// Variáveis globais para manter o estado dos filtros
let filtrosAtivos = {
    nome: '',
    prioridade: 'todas',
    status: 'todos',
    responsavel: 'todos'
};

// Funções para modais
function abrirModalTarefa() {
    document.getElementById('modalTarefa').style.display = 'block';
}

function fecharModalTarefa() {
    document.getElementById('modalTarefa').style.display = 'none';
}

function abrirModalMembros() {
    document.getElementById('modalMembros').style.display = 'block';
}

function fecharModalMembros() {
    document.getElementById('modalMembros').style.display = 'none';
}

function excluirProjeto() {
    document.getElementById('modalExcluirProjeto').style.display = 'block';
    // Fecha o menu dropdown
    const dropdown = document.getElementById('projetoMenuDropdown');
    dropdown.classList.remove('mostrar');
}

function fecharModalExcluir() {
    document.getElementById('modalExcluirProjeto').style.display = 'none';
}

// Novas funções para sair do projeto
function sairDoProjeto() {
    document.getElementById('modalSairProjeto').style.display = 'block';
    // Fecha o menu dropdown
    const dropdown = document.getElementById('projetoMenuDropdown');
    dropdown.classList.remove('mostrar');
}

function fecharModalSair() {
    document.getElementById('modalSairProjeto').style.display = 'none';
}

// Funções para membros
function adicionarMembro() {
    const email = document.getElementById('emailMembro').value;
    
    if (!email) {
        alert('Por favor, insira um email');
        return;
    }
    
    fetch(`/projeto/${getProjetoId()}/membros`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('convite enviado com sucesso!');
            location.reload();
        } else {
            alert('Erro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao adicionar membro');
    });
}

function removerMembro(usuarioId) {
    if (confirm('Tem certeza que deseja remover este membro do projeto?')) {
        fetch(`/projeto/${getProjetoId()}/membros/${usuarioId}/remover`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Membro removido com sucesso!');
            location.reload();
        } else {
            alert('Erro ao remover membro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao remover membro');
    });
    }
}

function excluirTarefa(tarefaId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        fetch(`/projeto/${getProjetoId()}/tarefa/${tarefaId}/excluir`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Tarefa excluída com sucesso!');
            location.reload();
        } else {
            alert('Erro ao excluir tarefa: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao excluir tarefa');
    });
    }
}

// Função para redirecionar para a página da tarefa
function redirecionarParaTarefa(tarefaId) {
    window.location.href = `/tarefa/${tarefaId}`;
}

// ================================
// SISTEMA DE FILTROS - CORRIGIDO
// ================================

function aplicarFiltros() {
    const filtroNome = document.getElementById('filtroNome').value.toLowerCase();
    const filtroPrioridade = document.getElementById('filtroPrioridade').value;
    const filtroStatus = document.getElementById('filtroStatus').value;
    const filtroResponsavel = document.getElementById('filtroResponsavel').value;
    
    // Atualizar estado dos filtros
    filtrosAtivos.nome = filtroNome;
    filtrosAtivos.prioridade = filtroPrioridade;
    filtrosAtivos.status = filtroStatus;
    filtrosAtivos.responsavel = filtroResponsavel;
    
    // Usar a classe correta dos cards (task-card-modern)
    const todasTarefas = document.querySelectorAll('.task-card-modern');
    let tarefasVisiveis = 0;
    
    console.log(`Aplicando filtros - Nome: ${filtroNome}, Prioridade: ${filtroPrioridade}, Status: ${filtroStatus}, Responsável: ${filtroResponsavel}`);
    console.log(`Total de tarefas encontradas: ${todasTarefas.length}`);
    
    todasTarefas.forEach(tarefa => {
        const titulo = tarefa.querySelector('h4').textContent.toLowerCase();
        const prioridade = tarefa.getAttribute('data-prioridade');
        const responsavel = tarefa.getAttribute('data-responsavel');
        const statusColuna = tarefa.closest('.tasks-list').getAttribute('data-status');
        
        let mostrar = true;
        
        // Aplicar filtro de nome
        if (filtroNome && !titulo.includes(filtroNome)) {
            mostrar = false;
        }
        
        // Aplicar filtro de prioridade
        if (filtroPrioridade !== 'todas' && prioridade !== filtroPrioridade) {
            mostrar = false;
        }
        
        // Aplicar filtro de status
        if (filtroStatus !== 'todos' && statusColuna !== filtroStatus) {
            mostrar = false;
        }
        
        // Aplicar filtro de responsável
        if (filtroResponsavel !== 'todos' && responsavel !== filtroResponsavel) {
            mostrar = false;
        }
        
        // Mostrar ou esconder a tarefa
        if (mostrar) {
            tarefa.style.display = 'block';
            tarefasVisiveis++;
        } else {
            tarefa.style.display = 'none';
        }
    });
    
    // Atualizar contadores das colunas
    atualizarContadoresColunas();
    
    console.log(`Filtros aplicados: ${tarefasVisiveis} tarefas visíveis`);
}

function limparFiltros() {
    document.getElementById('filtroNome').value = '';
    document.getElementById('filtroPrioridade').value = 'todas';
    document.getElementById('filtroStatus').value = 'todos';
    document.getElementById('filtroResponsavel').value = 'todos';
    
    // Resetar estado dos filtros
    filtrosAtivos = {
        nome: '',
        prioridade: 'todas',
        status: 'todos',
        responsavel: 'todos'
    };
    
    // Mostrar todas as tarefas
    const todasTarefas = document.querySelectorAll('.task-card-modern');
    todasTarefas.forEach(tarefa => {
        tarefa.style.display = 'block';
    });
    
    // Restaurar contadores originais
    atualizarContadoresColunas();
    
    console.log('Filtros limpos');
}

function atualizarContadoresColunas() {
    const colunas = document.querySelectorAll('.kanban-column');
    
    colunas.forEach(coluna => {
        const tasksList = coluna.querySelector('.tasks-list');
        const taskCountElement = coluna.querySelector('.task-count');
        
        // Contar apenas tarefas visíveis com a classe correta
        const tarefasVisiveis = tasksList.querySelectorAll('.task-card-modern[style="display: block"], .task-card-modern:not([style])').length;
        
        if (taskCountElement) {
            taskCountElement.textContent = tarefasVisiveis;
        }
    });
}

// ================================
// DRAG AND DROP FUNCTIONS - CORRIGIDO
// ================================

function allowDrop(ev) {
    ev.preventDefault();
}

function handleDragEnter(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.add('drag-over');
}

function handleDragLeave(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.remove('drag-over');
}

function drag(ev) {
    console.log('Iniciando drag da tarefa:', ev.target.dataset.taskId);
    ev.dataTransfer.setData("text", ev.target.dataset.taskId);
    // Usar a classe correta para dragging
    ev.target.classList.add('dragging');
}

function drop(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.remove('drag-over');
    
    // Encontrar o elemento correto da tarefa (pode ser o card ou um elemento filho)
    let targetElement = ev.target;
    while (targetElement && !targetElement.classList.contains('tasks-list')) {
        targetElement = targetElement.parentElement;
    }
    
    if (!targetElement) {
        console.error('Elemento tasks-list não encontrado');
        return;
    }
    
    const taskId = ev.dataTransfer.getData("text");
    const tasksList = targetElement;
    
    console.log(`Tentando mover tarefa ${taskId} para coluna:`, tasksList);
    
    // Remove dragging class from all task cards - CORRIGIDO para task-card-modern
    document.querySelectorAll('.task-card-modern.dragging').forEach(el => {
        el.classList.remove('dragging');
    });
    
    // Get the status from data-status attribute
    const newStatus = tasksList.getAttribute('data-status');
    
    if (!newStatus) {
        console.error('Status não encontrado na coluna');
        alert('Erro: Coluna não configurada corretamente');
        return;
    }
    
    console.log(`Movendo tarefa ${taskId} para status: ${newStatus}`);
    
    // Verificar se a tarefa já está no status correto
    const draggedElement = document.querySelector(`[data-task-id="${taskId}"]`);
    if (draggedElement) {
        const currentStatus = draggedElement.closest('.tasks-list').getAttribute('data-status');
        if (currentStatus === newStatus) {
            console.log('Tarefa já está no status correto, ignorando movimento');
            return;
        }
    }
    
    // Atualizar status no servidor
    fetch(`/projeto/${getProjetoId()}/tarefa/${taskId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro na resposta do servidor: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log('Status atualizado com sucesso');
            // Recarregar a página para refletir as mudanças
            location.reload();
        } else {
            alert('Erro ao atualizar tarefa: ' + (data.message || data.error || 'Erro desconhecido'));
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao atualizar tarefa: ' + error.message);
        location.reload();
    });
}

// Helper function to get projeto ID from URL
function getProjetoId() {
    const url = window.location.pathname;
    const matches = url.match(/\/projeto\/(\d+)/);
    return matches ? matches[1] : null;
}

// Funções para o menu do projeto
function toggleProjetoMenu() {
    const dropdown = document.getElementById('projetoMenuDropdown');
    dropdown.classList.toggle('mostrar');
}

// Remove drag-over class when drag ends - CORRIGIDO
document.addEventListener('dragend', function(ev) {
    console.log('Drag end event');
    document.querySelectorAll('.tasks-list.drag-over').forEach(el => {
        el.classList.remove('drag-over');
    });
    // Usar a classe correta para task-card-modern
    document.querySelectorAll('.task-card-modern.dragging').forEach(el => {
        el.classList.remove('dragging');
    });
});

// Prevenir comportamento padrão do dragover em todo o documento
document.addEventListener('dragover', function(ev) {
    ev.preventDefault();
});

function cancelarConvite(conviteId) {
    if (confirm('Tem certeza que deseja cancelar este convite?')) {
        fetch(`/projeto/${getProjetoId()}/convite/${conviteId}/cancelar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Convite cancelado com sucesso!');
                location.reload();
            } else {
                alert('Erro ao cancelar convite: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao cancelar convite');
        });
    }
}

// ================================
// SISTEMA DE EVENTOS CORRIGIDO - VERSÃO SIMPLIFICADA
// ================================

function inicializarEventListenersTarefas() {
    console.log('=== INICIALIZANDO EVENTOS DE TAREFAS ===');
    
    // ADICIONAR event listeners diretamente nos botões de ação
    document.querySelectorAll('.btn-acao-tarefa').forEach(button => {
        button.addEventListener('click', function(event) {
            console.log('Botão de ação clicado:', this);
            event.preventDefault();
            event.stopImmediatePropagation(); // Para IMEDIATAMENTE a propagação
            
            const taskId = this.getAttribute('data-task-id');
            const action = this.getAttribute('data-action');
            
            console.log(`Ação: ${action}, Tarefa ID: ${taskId}`);
            
            if (action === 'excluir') {
                excluirTarefa(taskId);
            } else if (action === 'editar') {
                editarTarefa(taskId);
            }
            
            // Retorna false para garantir que não propague
            return false;
        });
    });
    
    // Event listener para os CARDS (apenas áreas não-clicáveis)
    document.querySelectorAll('.task-card-modern').forEach(card => {
        card.addEventListener('click', function(event) {
            // Se o clique foi em qualquer botão ou elemento de ação, IGNORA
            if (event.target.closest('.btn-acao-tarefa') || 
                event.target.closest('.task-actions') ||
                event.target.matches('.btn-acao-tarefa') ||
                event.target.matches('.task-actions') ||
                event.target.matches('.task-actions *')) {
                console.log('Clique em elemento de ação - ignorando card');
                return;
            }
            
            // Só redireciona se foi clique direto no card ou em áreas não-interativas
            const taskId = this.dataset.taskId;
            if (taskId) {
                console.log('Redirecionando para tarefa:', taskId);
                redirecionarParaTarefa(taskId);
            }
        });
    });
}

// Função auxiliar para debug
function verificarBotoes() {
    const botoes = document.querySelectorAll('.btn-acao-tarefa, .task-actions button');
    console.log('=== BOTÕES ENCONTRADOS ===');
    botoes.forEach((btn, index) => {
        console.log(`Botão ${index + 1}:`, {
            elemento: btn,
            innerHTML: btn.innerHTML,
            classes: btn.className,
            'data-task-id': btn.getAttribute('data-task-id'),
            'data-action': btn.getAttribute('data-action')
        });
    });
    
    return botoes.length;
}

// ================================
// EVENT LISTENERS PRINCIPAIS - CORRIGIDO
// ================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('=== INICIALIZANDO SISTEMA DE PROJETOS ===');
    
    // Debug inicial
    setTimeout(() => {
        verificarBotoes();
    }, 100);
    
    // Inicializar event listeners específicos para tarefas
    inicializarEventListenersTarefas();

    // Fechar menu do projeto ao clicar fora
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('projetoMenuDropdown');
        const menuBtn = document.querySelector('.menu-btn');
        
        if (dropdown && menuBtn && !dropdown.contains(event.target) && !menuBtn.contains(event.target)) {
            dropdown.classList.remove('mostrar');
        }
    });

    // Fechar modais ao clicar fora
    window.onclick = function(event) {
        const modals = document.getElementsByClassName('modal');
        for (let modal of modals) {
            if (event.target == modal) {
                modal.style.display = 'none';
            }
        }
    };
    
    // Aplicar filtros iniciais
    aplicarFiltros();
    
    // Debug: verificar configuração das colunas
    console.log('=== CONFIGURAÇÃO DAS COLUNAS ===');
    const colunas = document.querySelectorAll('.tasks-list');
    colunas.forEach(coluna => {
        console.log('Coluna:', coluna.id, 'Status:', coluna.getAttribute('data-status'));
    });
    
    // Debug: verificar se os eventos de drag and drop estão configurados
    console.log('=== CONFIGURAÇÃO DRAG AND DROP ===');
    const taskCards = document.querySelectorAll('.task-card-modern');
    console.log(`Total de cards de tarefas: ${taskCards.length}`);
    taskCards.forEach((card, index) => {
        console.log(`Card ${index + 1}:`, {
            draggable: card.draggable,
            taskId: card.dataset.taskId,
            hasOndragstart: !!card.ondragstart
        });
    });
    
    console.log('=== SISTEMA DE PROJETOS INICIALIZADO ===');
});

// Funções para o modal de lista de membros
function abrirModalListaMembros() {
    document.getElementById('modalListaMembros').style.display = 'block';
}

function fecharModalListaMembros() {
    document.getElementById('modalListaMembros').style.display = 'none';
    // Fecha todos os menus abertos
    document.querySelectorAll('.menu-dropdown-membro').forEach(menu => {
        menu.classList.remove('mostrar');
    });
}

function toggleMembroMenu(usuarioId) {
    const menu = document.getElementById(`menuMembro${usuarioId}`);
    const todosMenus = document.querySelectorAll('.menu-dropdown-membro');
    
    // Fecha todos os outros menus
    todosMenus.forEach(m => {
        if (m !== menu) {
            m.classList.remove('mostrar');
        }
    });
    
    // Alterna o menu atual
    menu.classList.toggle('mostrar');
}

function tornarAdministrador(usuarioId) {
    if (confirm('Tem certeza que deseja tornar este membro administrador?\n\nAdministradores podem:\n• Criar e editar tarefas\n• Gerenciar membros\n• Alterar status de tarefas')) {
        fetch(`/projeto/${getProjetoId()}/membros/${usuarioId}/tornar-admin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Membro promovido a administrador com sucesso!');
                location.reload();
            } else {
                alert('Erro ao promover membro: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao promover membro');
        });
    }
}

function rebaixarMembro(usuarioId) {
    if (confirm('Tem certeza que deseja rebaixar este administrador?\n\nEle perderá as permissões de administrador.')) {
        fetch(`/projeto/${getProjetoId()}/membros/${usuarioId}/rebaixar-membro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Administrador rebaixado com sucesso!');
                location.reload();
            } else {
                alert('Erro ao rebaixar administrador: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao rebaixar administrador');
        });
    }
}

function removerMembroModal(usuarioId) {
    if (confirm('Tem certeza que deseja remover este membro do projeto?')) {
        fetch(`/projeto/${getProjetoId()}/membros/${usuarioId}/remover`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Membro removido com sucesso!');
                location.reload();
            } else {
                alert('Erro ao remover membro: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao remover membro');
        });
    }
}

// Fechar menus ao clicar fora
document.addEventListener('click', function(event) {
    // Fecha menus de membros
    document.querySelectorAll('.menu-dropdown-membro').forEach(menu => {
        if (!menu.contains(event.target) && !event.target.classList.contains('menu-btn-membro')) {
            menu.classList.remove('mostrar');
        }
    });
});