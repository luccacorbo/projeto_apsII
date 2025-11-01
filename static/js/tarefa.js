// Variáveis globais
let tarefaId = null;
let chatMessages = [];
let comentarioEditando = null;

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Obter o ID da tarefa da URL
    const pathParts = window.location.pathname.split('/');
    tarefaId = parseInt(pathParts[pathParts.length - 1]);
    
    if (isNaN(tarefaId)) {
        mostrarNotificacao('ID da tarefa inválido', 'error');
        return;
    }

    // Inicializar funcionalidades
    inicializarContadorCaracteres();
    carregarChat();
    
    // Fechar menu ao clicar fora
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.mensagem-acoes')) {
            fecharTodosMenus();
        }
    });
});

// Função para inicializar contador de caracteres
function inicializarContadorCaracteres() {
    const textarea = document.getElementById('novo-comentario-texto');
    const contador = document.getElementById('contador-caracteres');
    
    if (textarea && contador) {
        textarea.addEventListener('input', function() {
            const caracteresRestantes = 1000 - this.value.length;
            contador.textContent = caracteresRestantes;
            
            if (caracteresRestantes < 0) {
                contador.style.color = '#dc3545';
            } else if (caracteresRestantes < 100) {
                contador.style.color = '#ffc107';
            } else {
                contador.style.color = '#6c757d';
            }
        });
    }
}

// Função para carregar todo o chat (comentários + arquivos)
async function carregarChat() {
    if (!tarefaId) return;
    
    try {
        // Carregar comentários
        const comentariosResponse = await fetch(`/api/tarefas/${tarefaId}/comentarios`);
        if (!comentariosResponse.ok) throw new Error('Erro ao carregar comentários');
        const comentarios = await comentariosResponse.json();

        // Carregar arquivos
        const arquivosResponse = await fetch(`/api/tarefas/${tarefaId}/arquivos`);
        if (!arquivosResponse.ok) throw new Error('Erro ao carregar arquivos');
        const arquivos = await arquivosResponse.json();

        // Combinar e ordenar por data
        chatMessages = [
            ...comentarios.map(c => ({ ...c, tipo: 'comentario' })),
            ...arquivos.map(a => ({ ...a, tipo: 'arquivo' }))
        ].sort((a, b) => new Date(a.data_criacao || a.data_upload) - new Date(b.data_criacao || b.data_upload));

        exibirChat();
        
    } catch (error) {
        console.error('Erro ao carregar chat:', error);
        mostrarNotificacao('Erro ao carregar chat', 'error');
    }
}

// Função para exibir mensagens no chat
function exibirChat() {
    const container = document.getElementById('chat-messages');
    
    if (chatMessages.length === 0) {
        container.innerHTML = `
            <div class="empty-chat">
                <div class="empty-icon">💬</div>
                <h4>Nenhuma mensagem ainda</h4>
                <p>Seja o primeiro a comentar ou enviar um arquivo!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = chatMessages.map(mensagem => {
        if (mensagem.tipo === 'comentario') {
            return `
                <div class="mensagem-comentario" data-comentario-id="${mensagem.id_comentario}">
                    <div class="mensagem-header">
                        <div class="mensagem-usuario">
                            <div class="avatar-usuario">
                                ${mensagem.usuario_nome ? mensagem.usuario_nome.charAt(0).toUpperCase() : 'U'}
                            </div>
                            <div class="usuario-info">
                                <h5>${mensagem.usuario_nome || 'Usuário'}</h5>
                                <small>Comentário</small>
                            </div>
                        </div>
                        <div class="mensagem-data">${mensagem.data_criacao || ''}</div>
                    </div>
                    <div class="mensagem-texto">
                        ${mensagem.comentario || ''}
                    </div>
                    <div class="mensagem-acoes">
                        <button class="menu-toggle" onclick="toggleMenu(${mensagem.id_comentario})">
                            ⋮
                        </button>
                        <div class="menu-opcoes" id="menu-${mensagem.id_comentario}">
                            <button class="btn-editar" onclick="editarComentario(${mensagem.id_comentario})">
                            Editar
                            </button>
                            <button class="btn-excluir-comentario" onclick="excluirComentario(${mensagem.id_comentario})">
                            Excluir
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="mensagem-arquivo">
                    <div class="mensagem-header">
                        <div class="mensagem-usuario">
                            <div class="avatar-usuario">
                                ${mensagem.usuario_nome ? mensagem.usuario_nome.charAt(0).toUpperCase() : 'U'}
                            </div>
                            <div class="usuario-info">
                                <h5>${mensagem.usuario_nome || 'Usuário'}</h5>
                                <small>Arquivo enviado</small>
                            </div>
                        </div>
                        <div class="mensagem-data">${mensagem.data_upload || ''}</div>
                    </div>
                    <div class="arquivo-info">
                        <div class="arquivo-detalhes">
                            <div class="arquivo-nome">${mensagem.nome_arquivo || 'Arquivo sem nome'}</div>
                            <div class="arquivo-meta">
                                <span>📁 ${mensagem.tamanho_formatado || 'Tamanho desconhecido'}</span>
                                <span>📅 ${mensagem.data_upload || 'Data não disponível'}</span>
                            </div>
                        </div>
                        <div class="arquivo-acoes">
                            <button class="btn-download" onclick="downloadArquivo(${mensagem.id_arquivo})">
                                ⬇️
                            </button>
                            <button class="btn-excluir" onclick="excluirArquivo(${mensagem.id_arquivo})">
                                🗑️
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }).join('');
}

// Função para alternar o menu de opções
function toggleMenu(comentarioId) {
    fecharTodosMenus();
    
    const menu = document.getElementById(`menu-${comentarioId}`);
    if (menu) {
        menu.classList.toggle('mostrar');
    }
}

// Função para fechar todos os menus
function fecharTodosMenus() {
    const menus = document.querySelectorAll('.menu-opcoes');
    menus.forEach(menu => {
        menu.classList.remove('mostrar');
    });
}

// Função para editar comentário
function editarComentario(comentarioId) {
    fecharTodosMenus();
    
    const comentario = chatMessages.find(msg => 
        msg.tipo === 'comentario' && msg.id_comentario === comentarioId
    );
    
    if (!comentario) return;
    
    comentarioEditando = comentario;
    
    // Criar modal de edição
    const modalHtml = `
        <div class="modal-edicao mostrar" id="modal-edicao">
            <div class="modal-conteudo">
                <div class="modal-header">
                    <h3 class="modal-titulo">Editar Comentário</h3>
                    <button class="btn-fechar" onclick="fecharModalEdicao()">×</button>
                </div>
                <textarea class="modal-textarea" id="texto-edicao" maxlength="1000">${comentario.comentario || ''}</textarea>
                <div class="modal-acoes">
                    <button class="btn-cancelar" onclick="fecharModalEdicao()">Cancelar</button>
                    <button class="btn-salvar-edicao" onclick="salvarEdicaoComentario()">Salvar</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}

// Função para fechar modal de edição
function fecharModalEdicao() {
    const modal = document.getElementById('modal-edicao');
    if (modal) {
        modal.remove();
    }
    comentarioEditando = null;
}

// Função para salvar edição do comentário PERMANENTEMENTE
async function salvarEdicaoComentario() {
    if (!comentarioEditando || !tarefaId) return;
    
    const textoEditado = document.getElementById('texto-edicao').value.trim();
    
    if (!textoEditado) {
        mostrarNotificacao('O comentário não pode estar vazio', 'error');
        return;
    }
    
    try {
        const btn = document.querySelector('.btn-salvar-edicao');
        const textoOriginal = btn.textContent;
        btn.textContent = 'Salvando...';
        btn.disabled = true;
        
        const response = await fetch(`/api/tarefas/${tarefaId}/comentarios/${comentarioEditando.id_comentario}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ comentario: textoEditado })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao editar comentário');
        }
        
        const comentarioAtualizado = await response.json();
        
        // Atualizar no array local
        const index = chatMessages.findIndex(msg => 
            msg.tipo === 'comentario' && msg.id_comentario === comentarioEditando.id_comentario
        );
        
        if (index !== -1) {
            chatMessages[index] = { ...comentarioAtualizado, tipo: 'comentario' };
        }
        
        exibirChat();
        fecharModalEdicao();
        mostrarNotificacao('Comentário editado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao editar comentário:', error);
        mostrarNotificacao(`Erro: ${error.message}`, 'error');
        
        // Restaurar botão em caso de erro
        const btn = document.querySelector('.btn-salvar-edicao');
        btn.textContent = 'Salvar';
        btn.disabled = false;
    }
}

// Função para excluir comentário PERMANENTEMENTE
async function excluirComentario(comentarioId) {
    fecharTodosMenus();
    
    if (!confirm('Tem certeza que deseja excluir este comentário? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tarefas/${tarefaId}/comentarios/${comentarioId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir comentário');
        }
        
        // Remover do array local apenas se a exclusão foi bem-sucedida
        chatMessages = chatMessages.filter(msg => 
            !(msg.tipo === 'comentario' && msg.id_comentario === comentarioId)
        );
        
        exibirChat();
        mostrarNotificacao('Comentário excluído com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao excluir comentário:', error);
        mostrarNotificacao(`Erro: ${error.message}`, 'error');
    }
}

// Função para adicionar novo comentário
async function adicionarComentario() {
    if (!tarefaId) return;
    
    const textarea = document.getElementById('novo-comentario-texto');
    const comentario = textarea.value.trim();
    
    if (!comentario) {
        mostrarNotificacao('Por favor, digite um comentário', 'error');
        return;
    }
    
    if (comentario.length > 1000) {
        mostrarNotificacao('Comentário muito longo (máx. 1000 caracteres)', 'error');
        return;
    }
    
    try {
        const btn = document.querySelector('.btn-enviar');
        const textoOriginal = btn.textContent;
        btn.textContent = 'Enviando...';
        btn.disabled = true;
        
        const response = await fetch(`/api/tarefas/${tarefaId}/comentarios`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ comentario: comentario })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao adicionar comentário');
        }
        
        const novoComentario = await response.json();
        
        // Limpar campo
        textarea.value = '';
        document.getElementById('contador-caracteres').textContent = '1000';
        
        // Adicionar ao chat
        chatMessages.push({ ...novoComentario, tipo: 'comentario' });
        exibirChat();
        
        // Restaurar botão
        btn.textContent = textoOriginal;
        btn.disabled = false;
        
        mostrarNotificacao('Comentário adicionado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao adicionar comentário:', error);
        mostrarNotificacao(`Erro: ${error.message}`, 'error');
        
        // Restaurar botão em caso de erro
        const btn = document.querySelector('.btn-enviar');
        btn.textContent = '📝 Enviar';
        btn.disabled = false;
    }
}

// Função para fazer upload de arquivo
async function uploadArquivo() {
    if (!tarefaId) return;
    
    const input = document.getElementById('arquivo-upload');
    const arquivo = input.files[0];
    
    if (!arquivo) {
        mostrarNotificacao('Por favor, selecione um arquivo', 'error');
        return;
    }
    
    // Verificar tamanho do arquivo (16MB)
    if (arquivo.size > 16 * 1024 * 1024) {
        mostrarNotificacao('Arquivo muito grande (máx. 16MB)', 'error');
        return;
    }
    
    try {
        const btn = document.querySelector('.btn-upload');
        const textoOriginal = btn.textContent;
        btn.textContent = 'Enviando...';
        btn.disabled = true;
        
        const formData = new FormData();
        formData.append('arquivo', arquivo);
        
        const response = await fetch(`/api/tarefas/${tarefaId}/arquivos`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao fazer upload');
        }
        
        const novoArquivo = await response.json();
        
        // Limpar campo
        input.value = '';
        
        // Adicionar ao chat
        chatMessages.push({ ...novoArquivo, tipo: 'arquivo' });
        exibirChat();
        
        // Restaurar botão
        btn.textContent = textoOriginal;
        btn.disabled = false;
        
        mostrarNotificacao('Arquivo enviado com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao fazer upload:', error);
        mostrarNotificacao(`Erro: ${error.message}`, 'error');
        
        // Restaurar botão em caso de erro
        const btn = document.querySelector('.btn-upload');
        btn.textContent = '📎 Upload';
        btn.disabled = false;
    }
}

// Função para baixar arquivo - CORRIGIDA
function downloadArquivo(arquivoId) {
    // ✅ Use a rota correta que definimos no Flask
    window.open(`/api/tarefas/${tarefaId}/arquivos/${arquivoId}/download`, '_blank');
}

// Função para excluir arquivo PERMANENTEMENTE
async function excluirArquivo(arquivoId) {
    if (!confirm('Tem certeza que deseja excluir este arquivo? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tarefas/${tarefaId}/arquivos/${arquivoId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir arquivo');
        }
        
        // Remover do array local apenas se a exclusão foi bem-sucedida
        chatMessages = chatMessages.filter(msg => 
            !(msg.tipo === 'arquivo' && msg.id_arquivo === arquivoId)
        );
        
        exibirChat();
        mostrarNotificacao('Arquivo excluído com sucesso!', 'success');
        
    } catch (error) {
        console.error('Erro ao excluir arquivo:', error);
        mostrarNotificacao(`Erro: ${error.message}`, 'error');
    }
}

// Função para salvar alterações da tarefa (status)
async function salvarAlteracoes() {
    if (!tarefaId) {
        mostrarNotificacao('ID da tarefa não encontrado', 'error');
        return;
    }

    const status = document.getElementById('status').value;

    // Validação básica
    if (!status) {
        mostrarNotificacao('Por favor, selecione um status', 'error');
        return;
    }

    try {
        // Mostrar loading
        const salvarBtn = document.querySelector('.btn-salvar');
        const textoOriginal = salvarBtn.textContent;
        salvarBtn.textContent = 'Salvando...';
        salvarBtn.disabled = true;

        const response = await fetch(`/api/tarefas/${tarefaId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                status: status
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao atualizar tarefa');
        }

        // Restaurar botão
        salvarBtn.textContent = textoOriginal;
        salvarBtn.disabled = false;

        mostrarNotificacao('Tarefa atualizada com sucesso!', 'success');
        
        // Atualizar visualmente o status na página
        atualizarVisualizacaoStatus(status);
        
    } catch (error) {
        console.error('Erro:', error);
        
        // Restaurar botão em caso de erro
        const salvarBtn = document.querySelector('.btn-salvar');
        salvarBtn.textContent = 'Salvar Alterações';
        salvarBtn.disabled = false;
        
        mostrarNotificacao(`Erro ao atualizar tarefa: ${error.message}`, 'error');
    }
}

// Função para atualizar a visualização do status na página
function atualizarVisualizacaoStatus(novoStatus) {
    const card = document.querySelector('.tarefa-card');
    const statusBadge = document.querySelector('.status-badge');
    
    // Remover classes de status anteriores
    card.classList.remove('status-todo', 'status-doing', 'status-done');
    
    // Adicionar nova classe de status
    card.classList.add(`status-${novoStatus}`);
    
    // Atualizar texto do badge
    const statusText = {
        'todo': 'Pendente',
        'doing': 'Em Andamento',
        'done': 'Concluída'
    };
    
    statusBadge.textContent = statusText[novoStatus] || novoStatus;
    statusBadge.className = `status-badge status-${novoStatus}`;
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
    
    // Remover após 3 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// Event listeners
document.addEventListener('keydown', function(event) {
    // Ctrl+Enter para enviar comentário
    if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        adicionarComentario();
    }
});

// Event listener para mudança de status
document.getElementById('status').addEventListener('change', function() {
    // Feedback visual imediato
    atualizarVisualizacaoStatus(this.value);
});