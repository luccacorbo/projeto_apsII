// Variável global para armazenar tarefas
let tarefas = [];
let tarefasFiltradas = [];

// Carregar tarefas quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarTarefasDoBackend();
});

// Função para carregar tarefas do backend
async function carregarTarefasDoBackend() {
    try {
        mostrarLoading(true);
        
        const response = await fetch('/api/tarefas');
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        tarefas = data;
        tarefasFiltradas = [...tarefas];
        carregarTarefas();
        atualizarEstatisticas();
        mostrarLoading(false);
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao(`Erro ao carregar tarefas: ${error.message}`, 'error');
        mostrarLoading(false);
        mostrarEstadoVazio(true, 'Erro ao carregar tarefas');
    }
}

// Função para carregar tarefas no grid
function carregarTarefas() {
    const grid = document.getElementById('tarefas-grid');
    const emptyState = document.getElementById('empty-state');
    
    // Mostrar estado vazio se não houver tarefas
    if (tarefasFiltradas.length === 0) {
        grid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }
    
    grid.style.display = 'grid';
    emptyState.style.display = 'none';
    grid.innerHTML = '';
    
    tarefasFiltradas.forEach(tarefa => {
        const card = criarCardTarefa(tarefa);
        grid.appendChild(card);
    });
}

// Função para criar card de tarefa
function criarCardTarefa(tarefa) {
    const card = document.createElement('div');
    card.className = `tarefa-card status-${tarefa.status} prioridade-${tarefa.prioridade || 'media'}`;
    card.onclick = () => abrirModalTarefa(tarefa.id_tarefa);
    
    const statusIcon = getStatusIcon(tarefa.status);
    const prioridadeBadge = getPrioridadeBadge(tarefa.prioridade || 'media');
    
    card.innerHTML = `
        <div class="card-header">
            <span class="prioridade-badge">${prioridadeBadge}</span>
            <span class="status-icon">${statusIcon}</span>
        </div>
        <div class="card-body">
            <h3 class="card-titulo">${tarefa.titulo || 'Sem título'}</h3>
            <p class="card-descricao">${tarefa.descricao ? (tarefa.descricao.length > 100 ? tarefa.descricao.substring(0, 100) + '...' : tarefa.descricao) : 'Sem descrição'}</p>
            <div class="card-projeto">
                📁 ${tarefa.projeto_nome || 'Projeto não encontrado'}
            </div>
        </div>
        <div class="card-footer">
            <div class="card-info">
                <span class="info-item">
                    <strong>Responsável:</strong> ${tarefa.responsavel_nome || 'Você'}
                </span>
                <span class="info-item">
                    <strong>Prazo:</strong> ${tarefa.data_vencimento ? formatarData(tarefa.data_vencimento) : 'Sem prazo'}
                </span>
            </div>
            <div class="card-status">
                <span class="status-badge status-${tarefa.status}">
                    ${formatarStatus(tarefa.status)}
                </span>
            </div>
        </div>
    `;
    
    return card;
}

// Função para abrir modal com detalhes da tarefa
function abrirModalTarefa(tarefaId) {
    const tarefa = tarefas.find(t => t.id_tarefa === tarefaId);
    if (!tarefa) return;

    document.getElementById('task-id').value = tarefa.id_tarefa;
    document.getElementById('task-titulo').value = tarefa.titulo || '';
    document.getElementById('task-descricao').value = tarefa.descricao || '';
    document.getElementById('task-projeto').value = tarefa.projeto_nome || '';
    document.getElementById('task-prioridade').value = formatarPrioridade(tarefa.prioridade);
    document.getElementById('task-responsavel').value = tarefa.responsavel_nome || 'Você';
    document.getElementById('task-data-criacao').value = tarefa.data_criacao ? formatarDataCompleta(tarefa.data_criacao) : '';
    document.getElementById('task-data-vencimento').value = tarefa.data_vencimento ? formatarData(tarefa.data_vencimento) : 'Sem prazo';
    document.getElementById('task-status').value = tarefa.status || 'todo';
    document.getElementById('task-comentarios').value = tarefa.comentarios || '';

    // Atualizar estilo do status
    updateStatusStyle();

    document.getElementById('task-modal').style.display = 'block';
}

// Função para atualizar estilo do status no modal
function updateStatusStyle() {
    const statusSelect = document.getElementById('task-status');
    statusSelect.className = `status-${statusSelect.value}`;
}

// Função para fechar modal
function closeModal() {
    document.getElementById('task-modal').style.display = 'none';
}

// Função para salvar alterações da tarefa
async function saveTaskChanges() {
    const tarefaId = parseInt(document.getElementById('task-id').value);
    const novoStatus = document.getElementById('task-status').value;
    const comentarios = document.getElementById('task-comentarios').value;

    try {
        const response = await fetch(`/api/tarefas/${tarefaId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: novoStatus,
                comentarios: comentarios
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao atualizar tarefa');
        }

        // Atualizar a tarefa localmente
        const tarefaIndex = tarefas.findIndex(t => t.id_tarefa === tarefaId);
        if (tarefaIndex !== -1) {
            tarefas[tarefaIndex].status = novoStatus;
            tarefas[tarefaIndex].comentarios = comentarios;
            
            // Atualizar interface
            carregarTarefas();
            atualizarEstatisticas();
            closeModal();
            
            mostrarNotificacao('Tarefa atualizada com sucesso!', 'success');
            mostrarConfirmacao();
        }
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao(`Erro ao atualizar tarefa: ${error.message}`, 'error');
    }
}

// Função para atualizar estatísticas
function atualizarEstatisticas() {
    const total = tarefas.length;
    const pendentes = tarefas.filter(t => t.status === 'todo').length;
    const andamento = tarefas.filter(t => t.status === 'doing').length;
    const concluidas = tarefas.filter(t => t.status === 'done').length;

    document.getElementById('total-tasks').textContent = total;
    document.getElementById('pending-tasks').textContent = pendentes;
    document.getElementById('progress-tasks').textContent = andamento;
    document.getElementById('completed-tasks').textContent = concluidas;
}

// Funções de Filtro
function filterTasks() {
    const statusFilter = document.getElementById('filter-status').value;
    const priorityFilter = document.getElementById('filter-priority').value;

    tarefasFiltradas = tarefas.filter(tarefa => {
        const statusMatch = statusFilter === 'all' || tarefa.status === statusFilter;
        const priorityMatch = priorityFilter === 'all' || tarefa.prioridade === priorityFilter;
        
        return statusMatch && priorityMatch;
    });

    carregarTarefas();
}

function clearFilters() {
    document.getElementById('filter-status').value = 'all';
    document.getElementById('filter-priority').value = 'all';
    tarefasFiltradas = [...tarefas];
    carregarTarefas();
}

// Funções auxiliares
function getStatusIcon(status) {
    const icons = {
        'todo': '⏳',
        'doing': '🔄',
        'done': '✅'
    };
    return icons[status] || '📝';
}

function getPrioridadeBadge(prioridade) {
    const badges = {
        'alta': '🔥 ALTA',
        'media': '⚠️ MÉDIA',
        'baixa': '💤 BAIXA'
    };
    return badges[prioridade] || '📝 NORMAL';
}

function formatarStatus(status) {
    const statusMap = {
        'todo': 'Pendente',
        'doing': 'Em Andamento',
        'done': 'Concluída'
    };
    return statusMap[status] || status;
}

function formatarPrioridade(prioridade) {
    const prioridadeMap = {
        'alta': 'Alta',
        'media': 'Média',
        'baixa': 'Baixa'
    };
    return prioridadeMap[prioridade] || 'Média';
}

function formatarData(dataString) {
    if (!dataString) return 'Não definido';
    
    try {
        const data = new Date(dataString);
        if (isNaN(data.getTime())) {
            return 'Data inválida';
        }
        return data.toLocaleDateString('pt-BR');
    } catch (error) {
        return 'Data inválida';
    }
}

function formatarDataCompleta(dataString) {
    if (!dataString) return 'Não definida';
    
    try {
        const data = new Date(dataString);
        if (isNaN(data.getTime())) {
            return 'Data inválida';
        }
        return data.toLocaleString('pt-BR');
    } catch (error) {
        return 'Data inválida';
    }
}

// Funções de UI
function mostrarLoading(mostrar) {
    const loadingState = document.getElementById('loading-state');
    const grid = document.getElementById('tarefas-grid');
    const emptyState = document.getElementById('empty-state');
    
    if (mostrar) {
        loadingState.style.display = 'flex';
        grid.style.display = 'none';
        emptyState.style.display = 'none';
    } else {
        loadingState.style.display = 'none';
    }
}

function mostrarEstadoVazio(mostrar, mensagem = 'Nenhuma tarefa encontrada') {
    const emptyState = document.getElementById('empty-state');
    const grid = document.getElementById('tarefas-grid');
    
    if (mostrar) {
        if (mensagem !== 'Nenhuma tarefa encontrada') {
            emptyState.querySelector('h3').textContent = mensagem;
            emptyState.querySelector('p').textContent = 'Tente recarregar a página.';
        }
        emptyState.style.display = 'block';
        grid.style.display = 'none';
    } else {
        emptyState.style.display = 'none';
    }
}

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

function mostrarConfirmacao() {
    document.getElementById('confirmation-modal').style.display = 'block';
}

function closeConfirmationModal() {
    document.getElementById('confirmation-modal').style.display = 'none';
}

// Event Listeners
window.onclick = function(event) {
    const modal = document.getElementById('task-modal');
    const confirmModal = document.getElementById('confirmation-modal');
    
    if (event.target === modal) {
        closeModal();
    }
    if (event.target === confirmModal) {
        closeConfirmationModal();
    }
}

// Tecla ESC para fechar modais
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeModal();
        closeConfirmationModal();
    }
});