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
}

function fecharModalExcluir() {
    document.getElementById('modalExcluirProjeto').style.display = 'none';
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
            alert('Membro adicionado com sucesso!');
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

// Funções para tarefas
function editarTarefa(tarefaId) {
    alert('Funcionalidade de edição em desenvolvimento! Tarefa ID: ' + tarefaId);
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

// Drag and Drop Functions
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
    ev.dataTransfer.setData("text", ev.target.dataset.taskId);
    ev.target.classList.add('dragging');
}

function drop(ev) {
    ev.preventDefault();
    ev.currentTarget.classList.remove('drag-over');
    
    const taskId = ev.dataTransfer.getData("text");
    const tasksList = ev.currentTarget;
    
    // Remove dragging class from all task cards
    document.querySelectorAll('.task-card.dragging').forEach(el => {
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

// Fechar modais ao clicar fora e adicionar event listeners para tarefas
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar clique nos cards de tarefa
    document.addEventListener('click', function(event) {
        const taskCard = event.target.closest('.task-card');
        if (taskCard && !event.target.closest('.task-actions')) {
            const taskId = taskCard.dataset.taskId;
            if (taskId) {
                redirecionarParaTarefa(taskId);
            }
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
    
    // Debug: verificar configuração das colunas
    console.log('=== CONFIGURAÇÃO DAS COLUNAS ===');
    const colunas = document.querySelectorAll('.tasks-list');
    colunas.forEach(coluna => {
        console.log('Coluna:', coluna.id, 'Status:', coluna.getAttribute('data-status'));
    });
});

// Remove drag-over class when drag ends
document.addEventListener('dragend', function() {
    document.querySelectorAll('.tasks-list.drag-over').forEach(el => {
        el.classList.remove('drag-over');
    });
    document.querySelectorAll('.task-card.dragging').forEach(el => {
        el.classList.remove('dragging');
    });
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