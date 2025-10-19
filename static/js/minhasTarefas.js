// Variável global para armazenar tarefas
let tarefas = [];

// Carregar tarefas quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    carregarTarefasDoBackend();
});

// Função para carregar tarefas do backend
async function carregarTarefasDoBackend() {
    try {
        const response = await fetch('/api/tarefas');
        
        if (!response.ok) {
            throw new Error('Erro ao carregar tarefas');
        }
        
        tarefas = await response.json();
        carregarTarefas();
        atualizarEstatisticas();
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro ao carregar tarefas', 'error');
        
        // Mostrar estado vazio em caso de erro
        const grid = document.getElementById('tarefas-grid');
        grid.innerHTML = `
            <div class="empty-state">
                <h3>Erro ao carregar tarefas</h3>
                <p>Não foi possível carregar as tarefas do servidor.</p>
            </div>
        `;
    }
}

// Função para carregar tarefas no grid
function carregarTarefas() {
    const grid = document.getElementById('tarefas-grid');
    
    // Mostrar estado vazio se não houver tarefas
    if (tarefas.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <h3>Nenhuma tarefa encontrada</h3>
                <p>Você não tem tarefas atribuídas no momento.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = '';
    
    tarefas.forEach(tarefa => {
        const card = criarCardTarefa(tarefa);
        grid.appendChild(card);
    });
}

// Função para criar card de tarefa
function criarCardTarefa(tarefa) {
    const card = document.createElement('div');
    card.className = `tarefa-card status-${tarefa.status} prioridade-${tarefa.prioridade || 'media'}`;
    card.onclick = () => abrirModalTarefa(tarefa.id);
    
    const statusIcon = getStatusIcon(tarefa.status);
    const prioridadeBadge = getPrioridadeBadge(tarefa.prioridade || 'media');
    
    card.innerHTML = `
        <div class="card-header">
            <span class="prioridade-badge">${prioridadeBadge}</span>
            <span class="status-icon">${statusIcon}</span>
        </div>
        <div class="card-body">
            <h3 class="card-titulo">${tarefa.titulo || 'Sem título'}</h3>
            <p class="card-descricao">${tarefa.descricao ? tarefa.descricao.substring(0, 100) + '...' : 'Sem descrição'}</p>
        </div>
        <div class="card-footer">
            <div class="card-info">
                <span class="info-item">
                    <strong>Atribuída por:</strong> ${tarefa.atribuida_por || 'Não informado'}
                </span>
                <span class="info-item">
                    <strong>Prazo:</strong> ${tarefa.prazo ? formatarData(tarefa.prazo) : 'Sem prazo'}
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
    const tarefa = tarefas.find(t => t.id === tarefaId);
    if (!tarefa) return;

    document.getElementById('task-id').value = tarefa.id;
    document.getElementById('task-titulo').value = tarefa.titulo || '';
    document.getElementById('task-descricao').value = tarefa.descricao || '';
    document.getElementById('task-atribuida-por').value = tarefa.atribuida_por || '';
    document.getElementById('task-data-criacao').value = tarefa.data_criacao ? formatarData(tarefa.data_criacao) : '';
    document.getElementById('task-prazo').value = tarefa.prazo ? formatarData(tarefa.prazo) : '';
    document.getElementById('task-status').value = tarefa.status || 'pendente';
    document.getElementById('task-comentarios').value = tarefa.comentarios || '';

    document.getElementById('task-modal').style.display = 'block';
}

// Função para fechar modal
function closeModal() {
    document.getElementById('task-modal').style.display = 'none';
}

// Função para atualizar status da tarefa
function updateTaskStatus() {
    const statusSelect = document.getElementById('task-status');
    const novoStatus = statusSelect.value;
    
    console.log(`Status alterado para: ${novoStatus}`);
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

        if (!response.ok) {
            throw new Error('Erro ao atualizar tarefa');
        }

        // Atualizar a tarefa localmente
        const tarefaIndex = tarefas.findIndex(t => t.id === tarefaId);
        if (tarefaIndex !== -1) {
            tarefas[tarefaIndex].status = novoStatus;
            tarefas[tarefaIndex].comentarios = comentarios;
            
            // Atualizar interface
            carregarTarefas();
            atualizarEstatisticas();
            closeModal();
            
            mostrarNotificacao('Tarefa atualizada com sucesso!', 'success');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        mostrarNotificacao('Erro ao atualizar tarefa', 'error');
    }
}

// Função para atualizar estatísticas
function atualizarEstatisticas() {
    const total = tarefas.length;
    const pendentes = tarefas.filter(t => t.status === 'pendente').length;
    const andamento = tarefas.filter(t => t.status === 'andamento').length;
    const concluidas = tarefas.filter(t => t.status === 'concluida').length;

    document.getElementById('total-tasks').textContent = total;
    document.getElementById('pending-tasks').textContent = pendentes;
    document.getElementById('progress-tasks').textContent = andamento;
    document.getElementById('completed-tasks').textContent = concluidas;
}

// Função para mostrar notificações
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

// Funções auxiliares
function getStatusIcon(status) {
    const icons = {
        'pendente': '⏳',
        'andamento': '🔄',
        'concluida': '✅',
        'cancelada': '❌'
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
        'pendente': 'Pendente',
        'andamento': 'Em Andamento',
        'concluida': 'Concluída',
        'cancelada': 'Cancelada'
    };
    return statusMap[status] || status;
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

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('task-modal');
    if (event.target === modal) {
        closeModal();
    }
}