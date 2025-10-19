from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from database import conectar, close_db_connection

user = Blueprint('user', __name__)

# APIs de perfil
@user.route('/api/perfil')
def api_perfil():
    """API para buscar dados do perfil do usuário"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['usuario_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT nome, email FROM usuario WHERE id = %s', (usuario_id,))
        usuario = cursor.fetchone()
        
        if usuario:
            return jsonify({
                'nome': usuario['nome'],
                'email': usuario['email']
            })
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
            
    except Exception as e:
        print(f"Erro MySQL: {e}")
        return jsonify({'error': 'Erro ao buscar perfil'}), 500
    finally:
        close_db_connection(connection)

@user.route('/api/perfil/estatisticas')
def api_perfil_estatisticas():
    """API para buscar estatísticas do usuário"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['usuario_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Total de tarefas
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE usuario_id = %s', (usuario_id,))
        total_tarefas = cursor.fetchone()['total']
        
        # Tarefas pendentes
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE usuario_id = %s AND status = "pendente"', (usuario_id,))
        tarefas_pendentes = cursor.fetchone()['total']
        
        # Tarefas concluídas
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE usuario_id = %s AND status = "concluida"', (usuario_id,))
        tarefas_concluidas = cursor.fetchone()['total']
        
        # Dias ativo (exemplo simples)
        cursor.execute('SELECT data_criacao FROM usuario WHERE id = %s', (usuario_id,))
        resultado = cursor.fetchone()
        
        dias_ativo = 0
        if resultado and resultado['data_criacao']:
            from datetime import datetime
            data_criacao = resultado['data_criacao']
            dias_ativo = (datetime.now() - data_criacao).days
        
        return jsonify({
            'total_tarefas': total_tarefas,
            'tarefas_pendentes': tarefas_pendentes,
            'tarefas_concluidas': tarefas_concluidas,
            'dias_ativo': dias_ativo
        })
        
    except Exception as e:
        print(f"Erro MySQL: {e}")
        return jsonify({'error': 'Erro ao buscar estatísticas'}), 500
    finally:
        close_db_connection(connection)

@user.route('/api/perfil', methods=['PUT'])
def api_atualizar_perfil():
    """API para atualizar perfil do usuário"""
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['usuario_id']
    dados = request.get_json()
    
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    
    # Validar dados
    if not nome or not email:
        return jsonify({'error': 'Nome e email são obrigatórios'}), 400
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        
        if senha:
            # Se senha foi fornecida, atualizar com senha
            from werkzeug.security import generate_password_hash
            senha_hash = generate_password_hash(senha)
            
            cursor.execute('''
                UPDATE usuario 
                SET nome = %s, email = %s, senha = %s
                WHERE id = %s
            ''', (nome, email, senha_hash, usuario_id))
        else:
            # Se não, manter senha atual
            cursor.execute('''
                UPDATE usuarios 
                SET nome = %s, email = %s
                WHERE id = %s
            ''', (nome, email, usuario_id))
        
        connection.commit()
        
        # Atualizar sessão
        session['usuario_nome'] = nome
        session['usuario_email'] = email
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'usuario': {
                'nome': nome,
                'email': email
            }
        })
        
    except Exception as e:
        print(f"Erro MySQL: {e}")
        connection.rollback()
        
        # Verificar se é erro de duplicação de email
        if "Duplicate entry" in str(e):
            return jsonify({'error': 'Email já está em uso'}), 400
        else:
            return jsonify({'error': 'Erro ao atualizar perfil'}), 500
    finally:
        close_db_connection(connection)