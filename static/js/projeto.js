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

// Drag and Drop
function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    ev.dataTransfer.setData("text", ev.target.dataset.taskId);
}

function drop(ev) {
    ev.preventDefault();
    const taskId = ev.dataTransfer.getData("text");
    const newStatus = ev.target.id.split('-')[0]; // 'todo', 'doing', 'done'
    
    // Atualizar status no servidor
    fetch(`/projeto/{{ projeto.id_projeto }}/tarefa/${taskId}/status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    }).then(response => {
        if (response.ok) {
            location.reload(); // Recarregar para ver as mudanças
        }
    });
}

// Adicionar membro
function adicionarMembro() {
    const email = document.getElementById('emailMembro').value;
    
    if (!email) {
        alert('Por favor, insira um email');
        return;
    }
    
    fetch(`/projeto/{{ projeto.id_projeto }}/membros`, {
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
    });
}

// Fechar modais ao clicar fora
window.onclick = function(event) {
    const modals = document.getElementsByClassName('modal');
    for (let modal of modals) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

// Adicione estas funções ao seu projeto.js

// Excluir tarefa
function excluirTarefa(tarefaId) {
    if (confirm('Tem certeza que deseja excluir esta tarefa?')) {
        fetch(`/projeto/{{ projeto.id_projeto }}/tarefa/${tarefaId}/excluir`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Erro ao excluir tarefa: ' + data.error);
            }
        });
    }
}

// Remover membro
function removerMembro(usuarioId) {
    if (confirm('Tem certeza que deseja remover este membro do projeto?')) {
        fetch(`/projeto/{{ projeto.id_projeto }}/membros/${usuarioId}/remover`, {
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
        });
    }
}

// Editar tarefa (função básica - você pode expandir)
function editarTarefa(tarefaId) {
    alert('Funcionalidade de edição em desenvolvimento! Tarefa ID: ' + tarefaId);
    // Aqui você pode implementar um modal de edição similar ao de criação
}