from datetime import datetime, date
from flask import Blueprint, jsonify, redirect, request, session, url_for
from database import conectar, close_db_connection

task = Blueprint('task', __name__)


@task.route('/api/tarefas')
def api_tarefas():
    """API para buscar tarefas do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    id_usuario = session['user_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT t.*, p.nome as projeto_nome 
            FROM tarefas t 
            JOIN projetos p ON t.id_projeto = p.id_projeto 
            WHERE p.id_criador = %s OR t.id_responsavel = %s
            ORDER BY t.data_criacao DESC
        ''', (id_usuario, id_usuario))
        
        tarefas = cursor.fetchall()
        
        # Converter datetime para string para JSON
        for tarefa in tarefas:
            if tarefa['data_criacao']:
                tarefa['data_criacao'] = tarefa['data_criacao'].strftime('%Y-%m-%d %H:%M:%S')
            if tarefa['prazo']:
                tarefa['prazo'] = tarefa['prazo'].strftime('%Y-%m-%d')
        
        return jsonify(tarefas)
        
    except Exception as e:
        print(f"Erro MySQL: {e}")
        return jsonify({'error': 'Erro ao buscar tarefas'}), 500
    finally:
        close_db_connection(connection)


@task.route('/api/tarefas/<int:id_tarefa>', methods=['PUT'])
def api_atualizar_tarefa(id_tarefa):
    """API para atualizar uma tarefa"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    dados = request.get_json()
    novo_status = dados.get('status')
    comentarios = dados.get('comentarios', '')
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        
        # CORREÇÃO: Use 'user_id' da session e verifique se o usuário tem permissão
        # A consulta original usava 'id_usuario' que não existe na session
        cursor.execute('''
            UPDATE tarefas 
            SET status = %s, comentarios = %s
            WHERE id_tarefa = %s AND id_responsavel = %s
        ''', (novo_status, comentarios, id_tarefa, session['user_id']))
        
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tarefa não encontrada ou você não tem permissão para editá-la'}), 404
        
        return jsonify({'message': 'Tarefa atualizada com sucesso'})
        
    except Exception as e:
        print(f"Erro MySQL: {e}")
        connection.rollback()
        return jsonify({'error': 'Erro ao atualizar tarefa'}), 500
    finally:
        close_db_connection(connection)

'''
CRIAR E EXCLUIR TAREFAS 

'''

@task.route('/projeto/<int:id_projeto>/tarefa', methods=['POST'])
def criar_tarefa(id_projeto):
    if 'user_id' not in session:
        return redirect('/login')
    
    try:
        # Verificar se usuário tem permissão (criador ou membro)
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se usuário é criador ou membro do projeto
        cursor.execute("""
            SELECT 1 FROM projetos 
            WHERE id_projeto = %s AND id_criador = %s
            UNION
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
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
        
        # Converter data se fornecida (maneira mais segura)
        data_vencimento_sql = None
        if data_vencimento:
            try:
                # Converter string para objeto date
                data_obj = datetime.strptime(data_vencimento, '%Y-%m-%d').date()
                data_vencimento_sql = data_obj
            except ValueError as e:
                print(f"⚠️ Data inválida: {data_vencimento}, erro: {e}")
                # Continuar sem data de vencimento
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
        
        # Inserir tarefa
        cursor.execute("""
            INSERT INTO tarefas (titulo, descricao, prioridade, data_vencimento, id_projeto, id_criador, id_responsavel, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'todo')
        """, (titulo, descricao, prioridade, data_vencimento_sql, id_projeto, session['user_id'], id_responsavel))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"✅ Tarefa '{titulo}' criada com sucesso no projeto {id_projeto}")
        return redirect(url_for('work.visualizar_projeto', id_projeto=id_projeto))
        
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return f"Erro interno ao criar tarefa: {e}", 500
    

@task.route('/projeto/<int:id_projeto>/tarefa/<int:id_tarefa>/excluir', methods=['POST'])
def excluir_tarefa(id_projeto, id_tarefa):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se usuário é criador do projeto ou da tarefa
        cursor.execute("""
            SELECT p.id_criador as projeto_criador, t.id_criador as tarefa_criador
            FROM tarefas t
            JOIN projetos p ON t.id_projeto = p.id_projeto
            WHERE t.id_tarefa = %s AND t.id_projeto = %s
        """, (id_tarefa, id_projeto))
        
        resultado = cursor.fetchone()
        if not resultado:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        # Apenas criador do projeto ou da tarefa pode excluir
        if resultado['projeto_criador'] != session['user_id'] and resultado['tarefa_criador'] != session['user_id']:
            return jsonify({'error': 'Sem permissão para excluir esta tarefa'}), 403
        
        # Excluir tarefa
        cursor.execute("DELETE FROM tarefas WHERE id_tarefa = %s", (id_tarefa,))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro ao excluir tarefa: {e}")
        return jsonify({'error': 'Erro interno'}), 500
    