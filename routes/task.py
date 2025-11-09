from datetime import datetime, date
import os
from flask import Blueprint, jsonify, redirect, request, session, url_for, render_template, send_file
from werkzeug.utils import secure_filename
from database import conectar, close_db_connection

# Configurações para upload de arquivos
UPLOAD_FOLDER = 'uploads/tarefas'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Criar blueprint para rotas de tarefas
task = Blueprint('task', __name__)

def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def formatar_tamanho_arquivo(tamanho_bytes):
    """Formata o tamanho do arquivo para formato legível (B, KB, MB, GB)"""
    if tamanho_bytes < 1024:
        return f"{tamanho_bytes} B"
    elif tamanho_bytes < 1024 * 1024:
        return f"{tamanho_bytes / 1024:.1f} KB"
    elif tamanho_bytes < 1024 * 1024 * 1024:
        return f"{tamanho_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{tamanho_bytes / (1024 * 1024 * 1024):.1f} GB"

def formatar_status(status):
    """Formata o status para exibição amigável"""
    status_map = {
        'todo': 'Pendente',
        'doing': 'Em Andamento', 
        'done': 'Concluída'
    }
    return status_map.get(status, status)

def formatar_data(data_string):
    """Formata data para formato brasileiro (DD/MM/AAAA)"""
    if not data_string:
        return 'Não definido'
    try:
        if isinstance(data_string, str):
            data = datetime.strptime(data_string, '%Y-%m-%d')
        else:
            data = data_string
        return data.strftime('%d/%m/%Y')
    except:
        return 'Data inválida'

def formatar_data_completa(data_string):
    """Formata data e hora para formato brasileiro (DD/MM/AAAA HH:MM)"""
    if not data_string:
        return 'Não definida'
    try:
        if isinstance(data_string, str):
            data = datetime.strptime(data_string, '%Y-%m-%d %H:%M:%S')
        else:
            data = data_string
        return data.strftime('%d/%m/%Y %H:%M')
    except:
        return 'Data inválida'


@task.route('/api/tarefas')
def api_tarefas():
    """API para buscar todas as tarefas do usuário (como responsável, criador ou membro)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    id_usuario = session['user_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Consulta para buscar tarefas onde usuário é responsável, criador ou membro do projeto
        cursor.execute('''
            SELECT 
                t.id_tarefa,
                t.titulo,
                t.descricao,
                t.prioridade,
                t.status,
                t.data_criacao,
                t.data_vencimento,
                t.id_projeto,
                t.id_responsavel,
                p.nome as projeto_nome,
                u.nome as responsavel_nome
            FROM tarefas t 
            JOIN projetos p ON t.id_projeto = p.id_projeto 
            LEFT JOIN usuario u ON t.id_responsavel = u.id_usuario
            WHERE t.id_responsavel = %s 
               OR p.id_criador = %s
               OR EXISTS (
                   SELECT 1 FROM projeto_membros pm 
                   WHERE pm.id_projeto = p.id_projeto AND pm.id_usuario = %s
               )
            ORDER BY t.data_criacao DESC
        ''', (id_usuario, id_usuario, id_usuario))
        
        tarefas = cursor.fetchall()
        
        # Converter datetime para string para JSON
        for tarefa in tarefas:
            if tarefa['data_criacao']:
                if isinstance(tarefa['data_criacao'], (datetime, date)):
                    tarefa['data_criacao'] = tarefa['data_criacao'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    tarefa['data_criacao'] = str(tarefa['data_criacao'])
            
            if tarefa['data_vencimento']:
                if isinstance(tarefa['data_vencimento'], (datetime, date)):
                    tarefa['data_vencimento'] = tarefa['data_vencimento'].strftime('%Y-%m-%d')
                else:
                    tarefa['data_vencimento'] = str(tarefa['data_vencimento'])
        
        print(f"✅ Tarefas encontradas: {len(tarefas)}")
        return jsonify(tarefas)
        
    except Exception as e:
        print(f"❌ Erro MySQL na API de tarefas: {e}")
        return jsonify({'error': f'Erro ao buscar tarefas: {str(e)}'}), 500
    finally:
        close_db_connection(connection)


@task.route('/api/tarefas/<int:id_tarefa>', methods=['PUT'])
def api_atualizar_tarefa(id_tarefa):
    """API para atualizar status de uma tarefa"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Dados JSON inválidos'}), 400
    
    novo_status = dados.get('status')
    
    # ALTERAÇÃO: Removido o campo 'comentarios' que não existe mais na tabela tarefas
    # Comentários agora são gerenciados pela tabela separada 'comentarios'
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Verificação de permissões - usuário deve ser responsável, criador ou membro
        cursor.execute('''
            SELECT t.id_tarefa 
            FROM tarefas t
            LEFT JOIN projetos p ON t.id_projeto = p.id_projeto
            LEFT JOIN projeto_membros pm ON t.id_projeto = pm.id_projeto AND pm.id_usuario = %s
            WHERE t.id_tarefa = %s 
            AND (t.id_responsavel = %s OR p.id_criador = %s OR pm.id_usuario IS NOT NULL)
        ''', (session['user_id'], id_tarefa, session['user_id'], session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Tarefa não encontrada ou sem permissão'}), 404
        
        # ALTERAÇÃO: Atualizar apenas o status, removendo o campo comentarios
        cursor.execute('''
            UPDATE tarefas 
            SET status = %s
            WHERE id_tarefa = %s
        ''', (novo_status, id_tarefa))
        
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        return jsonify({'success': True, 'message': 'Tarefa atualizada com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro MySQL ao atualizar tarefa: {e}")
        connection.rollback()
        return jsonify({'error': f'Erro ao atualizar tarefa: {str(e)}'}), 500
    finally:
        close_db_connection(connection)


@task.route('/projeto/<int:id_projeto>/tarefa', methods=['POST'])
def criar_tarefa(id_projeto):
    """Rota para criar uma nova tarefa em um projeto"""
    if 'user_id' not in session:
        return redirect('/login')
    
    try:
        # Verificar se usuário tem permissão (criador, administrador OU membro do projeto)
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se usuário é criador, administrador ou membro do projeto
        cursor.execute("""
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s AND data_aceitacao IS NOT NULL
        """, (id_projeto, session['user_id'], id_projeto, session['user_id']))
        
        if not cursor.fetchone():
            return "Acesso negado", 403
        
        # Obter dados do formulário
        titulo = request.form.get('titulo', '').strip()
        descricao = request.form.get('descricao', '').strip()
        prioridade = request.form.get('prioridade', 'media')
        data_vencimento = request.form.get('data_vencimento')
        id_responsavel = request.form.get('id_responsavel', session['user_id'])
        
        # Validações
        if not titulo:
            return "Título da tarefa é obrigatório", 400
        
        # Converter data se fornecida
        data_vencimento_sql = None
        if data_vencimento:
            try:
                data_obj = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
                data_vencimento_sql = data_obj
            except ValueError as e:
                print(f"⚠️ Data inválida: {data_vencimento}, erro: {e}")
                data_vencimento_sql = None
        
        # Verificar se o responsável é membro do projeto
        if id_responsavel and int(id_responsavel) != session['user_id']:
            cursor.execute("""
                SELECT 1 FROM projeto_membros 
                WHERE id_projeto = %s AND id_usuario = %s
            """, (id_projeto, id_responsavel))
            if not cursor.fetchone():
                return "Usuário responsável não é membro do projeto", 400
        
        # Se id_responsavel não foi fornecido, usar o usuário atual
        if not id_responsavel:
            id_responsavel = session['user_id']
        
        # Inserir tarefa no banco
        cursor.execute("""
            INSERT INTO tarefas (titulo, descricao, prioridade, data_vencimento, id_projeto, id_criador, id_responsavel, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'todo')
        """, (titulo, descricao, prioridade, data_vencimento_sql, id_projeto, session['user_id'], id_responsavel))
        
        connection.commit()
        
        print(f"✅ Tarefa '{titulo}' criada com sucesso no projeto {id_projeto}")
        return redirect(url_for('work.visualizar_projeto', id_projeto=id_projeto))
        
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return f"Erro interno ao criar tarefa: {e}", 500
    finally:
        close_db_connection(connection)


@task.route('/projeto/<int:id_projeto>/tarefa/<int:id_tarefa>/excluir', methods=['POST'])
def excluir_tarefa(id_projeto, id_tarefa):
    """Rota para excluir uma tarefa"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    connection = None
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se usuário é criador do projeto, administrador ou da tarefa
        cursor.execute("""
            SELECT p.id_criador as projeto_criador, t.id_criador as tarefa_criador,
                   pm.eh_administrador
            FROM tarefas t
            JOIN projetos p ON t.id_projeto = p.id_projeto
            LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto AND pm.id_usuario = %s
            WHERE t.id_tarefa = %s AND t.id_projeto = %s
        """, (session['user_id'], id_tarefa, id_projeto))
        
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Apenas criador do projeto, administrador ou criador da tarefa pode excluir
        if (resultado['projeto_criador'] != session['user_id'] and 
            not resultado['eh_administrador'] and 
            resultado['tarefa_criador'] != session['user_id']):
            return jsonify({'error': 'Sem permissão para excluir esta tarefa'}), 403
        
        # Excluir tarefa
        cursor.execute("DELETE FROM tarefas WHERE id_tarefa = %s", (id_tarefa,))
        connection.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro ao excluir tarefa: {e}")
        if connection:
            connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        if connection:
            close_db_connection(connection)


@task.route('/api/minhas-tarefas')
def api_minhas_tarefas():
    """API para buscar APENAS tarefas onde o usuário é o RESPONSÁVEL"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    id_usuario = session['user_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT 
                t.id_tarefa,
                t.titulo,
                t.descricao,
                t.prioridade,
                t.status,
                t.data_criacao,
                t.data_vencimento,
                t.id_projeto,
                t.id_responsavel,
                p.nome as projeto_nome,
                u.nome as responsavel_nome
            FROM tarefas t 
            JOIN projetos p ON t.id_projeto = p.id_projeto 
            LEFT JOIN usuario u ON t.id_responsavel = u.id_usuario
            WHERE t.id_responsavel = %s  -- ⚠️ APENAS tarefas onde usuário é responsável
            ORDER BY t.data_criacao DESC
        ''', (id_usuario,))
        
        tarefas = cursor.fetchall()
        
        # Converter datetime para string
        for tarefa in tarefas:
            if tarefa['data_criacao'] and isinstance(tarefa['data_criacao'], (datetime, date)):
                tarefa['data_criacao'] = tarefa['data_criacao'].strftime('%Y-%m-%d %H:%M:%S')
            if tarefa['data_vencimento'] and isinstance(tarefa['data_vencimento'], (datetime, date)):
                tarefa['data_vencimento'] = tarefa['data_vencimento'].strftime('%Y-%m-%d')
        
        print(f"✅ Minhas Tarefas (responsável): {len(tarefas)}")
        return jsonify(tarefas)
        
    except Exception as e:
        print(f"❌ Erro MySQL na API de minhas tarefas: {e}")
        return jsonify({'error': f'Erro ao buscar tarefas: {str(e)}'}), 500
    finally:
        close_db_connection(connection)


@task.route('/tarefa/<int:tarefa_id>')
def detalhes_tarefa(tarefa_id):
    """Página de detalhes de uma tarefa específica - ACESSO PARA QUALQUER MEMBRO DO PROJETO"""
    if 'user_id' not in session:
        return redirect('/login')
    
    connection = conectar()
    if not connection:
        return "Erro de conexão com o banco", 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ALTERAÇÃO: Buscar dados da tarefa e verificar se usuário é membro do projeto
        cursor.execute('''
            SELECT 
                t.id_tarefa,
                t.titulo,
                t.descricao,
                t.prioridade,
                t.status,
                t.data_criacao,
                t.data_vencimento,
                t.id_projeto,
                t.id_responsavel,
                t.id_criador,
                p.nome as projeto_nome,
                p.id_criador as projeto_criador,
                u.nome as responsavel_nome,
                uc.nome as criador_nome
            FROM tarefas t 
            JOIN projetos p ON t.id_projeto = p.id_projeto 
            LEFT JOIN usuario u ON t.id_responsavel = u.id_usuario
            LEFT JOIN usuario uc ON t.id_criador = uc.id_usuario
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        
        if not tarefa:
            return "Tarefa não encontrada", 404
        
        # ALTERAÇÃO: Verificar se usuário é membro do projeto (criador ou membro adicionado)
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return "Acesso negado: você não é membro deste projeto", 403
        
        # ALTERAÇÃO: Buscar comentários da tabela separada 'comentarios'
        cursor.execute('''
            SELECT c.*, u.nome as usuario_nome
            FROM comentarios c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            WHERE c.id_tarefa = %s
            ORDER BY c.data_comentario ASC
        ''', (tarefa_id,))
        comentarios = cursor.fetchall()
        tarefa['comentarios'] = comentarios
        
        # ALTERAÇÃO: Buscar arquivos da tabela separada 'arquivos'
        cursor.execute('''
            SELECT a.*, u.nome as usuario_nome
            FROM arquivos a
            JOIN usuario u ON a.id_usuario = u.id_usuario
            WHERE a.id_tarefa = %s
            ORDER BY a.data_upload DESC
        ''', (tarefa_id,))
        arquivos = cursor.fetchall()
        tarefa['arquivos'] = arquivos
        
        # Buscar primeiro nome do usuário para o header
        cursor.execute('SELECT nome FROM usuario WHERE id_usuario = %s', (session['user_id'],))
        usuario = cursor.fetchone()
        primeiro_nome = usuario['nome'].split(' ')[0] if usuario and usuario['nome'] else 'Usuário'
        
        return render_template('tarefa.html', 
                             tarefa=tarefa,
                             primeiro_nome=primeiro_nome,
                             formatar_status=formatar_status,
                             formatar_data=formatar_data,
                             formatar_data_completa=formatar_data_completa)
        
    except Exception as e:
        print(f"❌ Erro ao carregar detalhes da tarefa: {e}")
        return f"Erro interno: {str(e)}", 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefa/<int:tarefa_id>')
def api_tarefa_especifica(tarefa_id):
    """API para buscar uma tarefa específica - ACESSO PARA QUALQUER MEMBRO DO PROJETO"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ALTERAÇÃO: Buscar dados da tarefa
        cursor.execute('''
            SELECT 
                t.id_tarefa,
                t.titulo,
                t.descricao,
                t.prioridade,
                t.status,
                t.data_criacao,
                t.data_vencimento,
                t.id_projeto,
                t.id_responsavel
            FROM tarefas t 
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # ALTERAÇÃO: Verificar se usuário é membro do projeto
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Acesso negado: você não é membro deste projeto'}), 403
        
        # Converter datetime para string
        if tarefa['data_criacao'] and isinstance(tarefa['data_criacao'], (datetime, date)):
            tarefa['data_criacao'] = tarefa['data_criacao'].strftime('%Y-%m-%d %H:%M:%S')
        if tarefa['data_vencimento'] and isinstance(tarefa['data_vencimento'], (datetime, date)):
            tarefa['data_vencimento'] = tarefa['data_vencimento'].strftime('%Y-%m-%d')
        
        return jsonify(tarefa)
        
    except Exception as e:
        print(f"❌ Erro MySQL ao buscar tarefa específica: {e}")
        return jsonify({'error': f'Erro ao buscar tarefa: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/comentarios', methods=['GET', 'POST'])
def api_comentarios_tarefa(tarefa_id):
    """API para gerenciar comentários da tarefa - ACESSO PARA QUALQUER MEMBRO DO PROJETO"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ALTERAÇÃO: Verificar se usuário é membro do projeto da tarefa
        cursor.execute('''
            SELECT t.id_projeto 
            FROM tarefas t
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Verificar se usuário é membro do projeto
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Acesso negado: você não é membro deste projeto'}), 403
        
        if request.method == 'GET':
            # Buscar comentários da tabela 'comentarios'
            cursor.execute('''
                SELECT 
                    c.id_comentario,
                    c.comentario,
                    c.data_comentario as data_criacao,
                    c.id_usuario,
                    u.nome as usuario_nome
                FROM comentarios c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                WHERE c.id_tarefa = %s
                ORDER BY c.data_comentario ASC
            ''', (tarefa_id,))
            
            comentarios = cursor.fetchall()
            
            # Formatar datas
            for comentario in comentarios:
                if comentario['data_criacao']:
                    comentario['data_criacao'] = comentario['data_criacao'].strftime('%d/%m/%Y %H:%M')
            
            return jsonify(comentarios)
            
        elif request.method == 'POST':
            # Adicionar novo comentário - QUALQUER MEMBRO DO PROJETO PODE ADICIONAR
            dados = request.get_json()
            if not dados or not dados.get('comentario'):
                return jsonify({'error': 'Comentário é obrigatório'}), 400
            
            comentario = dados['comentario'].strip()
            if not comentario:
                return jsonify({'error': 'Comentário não pode estar vazio'}), 400
            
            # Inserir na tabela 'comentarios'
            cursor.execute('''
                INSERT INTO comentarios (id_tarefa, id_usuario, comentario)
                VALUES (%s, %s, %s)
            ''', (tarefa_id, session['user_id'], comentario))
            
            connection.commit()
            
            # Retornar o comentário criado
            cursor.execute('''
                SELECT 
                    c.id_comentario,
                    c.comentario,
                    c.data_comentario as data_criacao,
                    c.id_usuario,
                    u.nome as usuario_nome
                FROM comentarios c
                JOIN usuario u ON c.id_usuario = u.id_usuario
                WHERE c.id_comentario = LAST_INSERT_ID()
            ''')
            
            novo_comentario = cursor.fetchone()
            if novo_comentario['data_criacao']:
                novo_comentario['data_criacao'] = novo_comentario['data_criacao'].strftime('%d/%m/%Y %H:%M')
            
            return jsonify(novo_comentario)
            
    except Exception as e:
        print(f"❌ Erro ao gerenciar comentários: {e}")
        if request.method == 'POST':
            connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)


    """API para excluir comentário permanentemente"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se o comentário existe e se o usuário é o dono
        cursor.execute('''
            SELECT c.id_comentario, c.id_usuario 
            FROM comentarios c
            WHERE c.id_comentario = %s AND c.id_tarefa = %s
        ''', (comentario_id, tarefa_id))
        
        comentario = cursor.fetchone()
        if not comentario:
            return jsonify({'error': 'Comentário não encontrado'}), 404
        
        # Verificar se usuário é o dono do comentário ou responsável pela tarefa
        cursor.execute('''
            SELECT 1 FROM tarefas 
            WHERE id_tarefa = %s AND (id_responsavel = %s OR %s IN (id_responsavel, id_criador))
        ''', (tarefa_id, session['user_id'], comentario['id_usuario']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Sem permissão para excluir este comentário'}), 403
        
        # Excluir comentário permanentemente
        cursor.execute('DELETE FROM comentarios WHERE id_comentario = %s', (comentario_id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Comentário excluído com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro ao excluir comentário: {e}")
        connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/arquivos', methods=['GET', 'POST'])
def api_arquivos_tarefa(tarefa_id):
    """API para gerenciar arquivos da tarefa - ACESSO PARA QUALQUER MEMBRO DO PROJETO"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ✅ CORREÇÃO: Verificar se usuário é membro do projeto da tarefa
        cursor.execute('''
            SELECT t.id_projeto 
            FROM tarefas t
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # ✅ CORREÇÃO: Verificar se usuário é membro do projeto (criador ou membro adicionado)
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Acesso negado: você não é membro deste projeto'}), 403
        
        # Resto do código permanece igual...
        if request.method == 'GET':
            cursor.execute('''
                SELECT 
                    a.id_arquivo,
                    a.nome_arquivo,
                    a.caminho_arquivo,
                    a.tamanho,
                    a.tipo_arquivo,
                    a.data_upload,
                    a.id_usuario,
                    u.nome as usuario_nome
                FROM arquivos a
                JOIN usuario u ON a.id_usuario = u.id_usuario
                WHERE a.id_tarefa = %s
                ORDER BY a.data_upload DESC
            ''', (tarefa_id,))
            
            arquivos = cursor.fetchall()
            
            # Formatar dados
            for arquivo in arquivos:
                if arquivo['data_upload']:
                    arquivo['data_upload'] = arquivo['data_upload'].strftime('%d/%m/%Y %H:%M')
                if arquivo['tamanho']:
                    arquivo['tamanho_formatado'] = formatar_tamanho_arquivo(arquivo['tamanho'])
            
            return jsonify(arquivos)
            
        elif request.method == 'POST':
            # Upload de arquivo - QUALQUER MEMBRO DO PROJETO PODE FAZER UPLOAD
            if 'arquivo' not in request.files:
                return jsonify({'error': 'Nenhum arquivo enviado'}), 400
            
            arquivo = request.files['arquivo']
            if arquivo.filename == '':
                return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
            
            if arquivo and allowed_file(arquivo.filename):
                # Verificar tamanho do arquivo
                arquivo.seek(0, 2)
                tamanho = arquivo.tell()
                arquivo.seek(0)
                
                if tamanho > MAX_FILE_SIZE:
                    return jsonify({'error': f'Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024*1024)}MB'}), 400
                
                # Criar diretório se não existir
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Gerar nome seguro para o arquivo
                filename = secure_filename(arquivo.filename)
                nome_unico = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_unico)
                
                # Salvar arquivo
                arquivo.save(caminho_arquivo)
                
                cursor.execute('''
                    INSERT INTO arquivos (id_tarefa, id_usuario, nome_arquivo, caminho_arquivo, tamanho, tipo_arquivo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (tarefa_id, session['user_id'], filename, caminho_arquivo, tamanho, arquivo.content_type))
                
                connection.commit()
                
                # Retornar dados do arquivo
                cursor.execute('''
                    SELECT 
                        a.id_arquivo,
                        a.nome_arquivo,
                        a.caminho_arquivo,
                        a.tamanho,
                        a.tipo_arquivo,
                        a.data_upload,
                        a.id_usuario,
                        u.nome as usuario_nome
                    FROM arquivos a
                    JOIN usuario u ON a.id_usuario = u.id_usuario
                    WHERE a.id_arquivo = LAST_INSERT_ID()
                ''')
                
                novo_arquivo = cursor.fetchone()
                if novo_arquivo['data_upload']:
                    novo_arquivo['data_upload'] = novo_arquivo['data_upload'].strftime('%d/%m/%Y %H:%M')
                if novo_arquivo['tamanho']:
                    novo_arquivo['tamanho_formatado'] = formatar_tamanho_arquivo(novo_arquivo['tamanho'])
                
                return jsonify(novo_arquivo)
            else:
                return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
            
    except Exception as e:
        print(f"❌ Erro ao gerenciar arquivos: {e}")
        if request.method == 'POST':
            connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/comentarios/<int:comentario_id>', methods=['PUT'])
def api_editar_comentario(tarefa_id, comentario_id):
    """API para editar comentário permanentemente"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    dados = request.get_json()
    if not dados or not dados.get('comentario'):
        return jsonify({'error': 'Comentário é obrigatório'}), 400
    
    novo_comentario = dados['comentario'].strip()
    if not novo_comentario:
        return jsonify({'error': 'Comentário não pode estar vazio'}), 400
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se o comentário existe e se o usuário é o dono
        cursor.execute('''
            SELECT c.id_comentario, c.id_usuario 
            FROM comentarios c
            WHERE c.id_comentario = %s AND c.id_tarefa = %s
        ''', (comentario_id, tarefa_id))
        
        comentario = cursor.fetchone()
        if not comentario:
            return jsonify({'error': 'Comentário não encontrado'}), 404
        
        # Verificar se usuário é o dono do comentário
        if comentario['id_usuario'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para editar este comentário'}), 403
        
        # Atualizar comentário
        cursor.execute('''
            UPDATE comentarios 
            SET comentario = %s, data_comentario = CURRENT_TIMESTAMP
            WHERE id_comentario = %s
        ''', (novo_comentario, comentario_id))
        
        connection.commit()
        
        # Buscar comentário atualizado
        cursor.execute('''
            SELECT 
                c.id_comentario,
                c.comentario,
                c.data_comentario as data_criacao,
                c.id_usuario,
                u.nome as usuario_nome
            FROM comentarios c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            WHERE c.id_comentario = %s
        ''', (comentario_id,))
        
        comentario_atualizado = cursor.fetchone()
        
        return jsonify(comentario_atualizado)
        
    except Exception as e:
        print(f"❌ Erro ao editar comentário: {e}")
        connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/arquivos/<int:arquivo_id>', methods=['DELETE'])
def api_excluir_arquivos_tarefa(tarefa_id, arquivo_id):
    """API para excluir arquivo - APENAS O USUÁRIO QUE ANEXOU"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ✅ PRIMEIRO verificar se usuário é membro do projeto
        cursor.execute('''
            SELECT t.id_projeto 
            FROM tarefas t
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        if not tarefa:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # ✅ Verificar se usuário é membro do projeto
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Acesso negado: você não é membro deste projeto'}), 403
        
        # ✅ DEPOIS buscar informações do arquivo
        cursor.execute('''
            SELECT a.caminho_arquivo, a.id_usuario
            FROM arquivos a
            WHERE a.id_arquivo = %s AND a.id_tarefa = %s
        ''', (arquivo_id, tarefa_id))
        
        arquivo = cursor.fetchone()
        if not arquivo:
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        # ✅ Verificar permissão: APENAS o usuário que fez o upload pode excluir
        if arquivo['id_usuario'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para excluir este arquivo'}), 403
        
        # Excluir arquivo físico
        try:
            if os.path.exists(arquivo['caminho_arquivo']):
                os.remove(arquivo['caminho_arquivo'])
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível excluir o arquivo físico: {e}")
        
        # Excluir registro do banco
        cursor.execute('DELETE FROM arquivos WHERE id_arquivo = %s', (arquivo_id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Arquivo excluído com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro ao excluir arquivo: {e}")
        connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/comentarios/<int:comentario_id>', methods=['DELETE'])
def api_excluir_comentario(tarefa_id, comentario_id):
    """API para excluir comentário - APENAS O USUÁRIO QUE COMENTOU"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Buscar informações do comentário
        cursor.execute('''
            SELECT c.id_usuario
            FROM comentarios c
            WHERE c.id_comentario = %s AND c.id_tarefa = %s
        ''', (comentario_id, tarefa_id))
        
        comentario = cursor.fetchone()
        if not comentario:
            return jsonify({'error': 'Comentário não encontrado'}), 404
        
        # Verificar permissão: APENAS o dono do comentário pode excluir
        if comentario['id_usuario'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para excluir este comentário'}), 403
        
        # Excluir comentário
        cursor.execute('DELETE FROM comentarios WHERE id_comentario = %s', (comentario_id,))
        connection.commit()
        
        return jsonify({'success': True, 'message': 'Comentário excluído com sucesso'})
        
    except Exception as e:
        print(f"❌ Erro ao excluir comentário: {e}")
        connection.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
    finally:
        close_db_connection(connection)

@task.route('/api/tarefas/<int:tarefa_id>/arquivos/<int:arquivo_id>/download')
def download_arquivo(tarefa_id, arquivo_id):
    """Rota para download de arquivos - ACESSO PARA QUALQUER MEMBRO DO PROJETO"""
    if 'user_id' not in session:
        return redirect('/login')
    
    connection = conectar()
    if not connection:
        return "Erro de conexão com o banco", 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ✅ Verificar se usuário é membro do projeto da tarefa
        cursor.execute('''
            SELECT t.id_projeto 
            FROM tarefas t
            WHERE t.id_tarefa = %s
        ''', (tarefa_id,))
        
        tarefa = cursor.fetchone()
        if not tarefa:
            return "Tarefa não encontrada", 404
        
        # ✅ Verificar se usuário é membro do projeto (criador ou membro adicionado)
        cursor.execute('''
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        ''', (tarefa['id_projeto'], session['user_id'], tarefa['id_projeto'], session['user_id']))
        
        if not cursor.fetchone():
            return "Acesso negado: você não é membro deste projeto", 403
        
        # Buscar informações do arquivo
        cursor.execute('''
            SELECT a.nome_arquivo, a.caminho_arquivo, a.tipo_arquivo
            FROM arquivos a
            WHERE a.id_arquivo = %s AND a.id_tarefa = %s
        ''', (arquivo_id, tarefa_id))
        
        arquivo = cursor.fetchone()
        if not arquivo:
            return "Arquivo não encontrado", 404
        
        # Verificar se o arquivo físico existe
        if not os.path.exists(arquivo['caminho_arquivo']):
            return "Arquivo não encontrado no servidor", 404
        
        # Fazer download do arquivo
        return send_file(
            arquivo['caminho_arquivo'],
            as_attachment=True,
            download_name=arquivo['nome_arquivo'],
            mimetype=arquivo['tipo_arquivo']
        )
        
    except Exception as e:
        print(f"❌ Erro ao fazer download do arquivo: {e}")
        return f"Erro interno: {str(e)}", 500
    finally:
        close_db_connection(connection)