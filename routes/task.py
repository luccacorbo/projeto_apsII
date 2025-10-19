from flask import Blueprint, jsonify, request, session
from database import conectar, close_db_connection

task = Blueprint('task', __name__)


@task.route('/api/tarefas')
def api_tarefas():
    """API para buscar tarefas do usuário"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['usuario_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('''
            SELECT * FROM tarefas 
            WHERE usuario_id = %s 
            ORDER BY data_criacao DESC
        ''', (usuario_id,))
        
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

@task.route('/api/tarefas/<int:tarefa_id>', methods=['PUT'])
def api_atualizar_tarefa(tarefa_id):
    """API para atualizar uma tarefa"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    dados = request.get_json()
    novo_status = dados.get('status')
    comentarios = dados.get('comentarios', '')
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute('''
            UPDATE tarefas 
            SET status = %s, comentarios = %s
            WHERE id = %s AND usuario_id = %s
        ''', (novo_status, comentarios, tarefa_id, session['usuario_id']))
        
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({'error': 'Tarefa não encontrada'}), 404
        
        return jsonify({'message': 'Tarefa atualizada com sucesso'})
        
    except Exception as e:
        print(f"Erro MySQL: {e}")
        connection.rollback()
        return jsonify({'error': 'Erro ao atualizar tarefa'}), 500