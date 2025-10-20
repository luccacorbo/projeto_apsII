from flask import Blueprint, jsonify, request, session
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