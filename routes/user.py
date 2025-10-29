from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from database import conectar, close_db_connection

user = Blueprint('user', __name__)

# APIs de perfil
@user.route('/api/perfil')
def api_perfil():
    """API para buscar dados do perfil do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['user_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # CORREÇÃO: Use o nome correto da coluna baseado na sua estrutura real
        # Possíveis nomes: id_usuario, user_id, usuario_id, id
        cursor.execute('SELECT nome, email FROM usuario WHERE id_usuario = %s', (usuario_id,))
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
    """API para buscar estatísticas do usuário - APENAS tarefas onde é RESPONSÁVEL"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['user_id']
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # ✅ CORREÇÃO: Buscar APENAS tarefas onde o usuário é o RESPONSÁVEL
        # Total de tarefas - onde usuário é responsável
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE id_responsavel = %s', (usuario_id,))
        total_tarefas = cursor.fetchone()['total']
        
        # ✅ CORREÇÃO: Usar os status corretos (todo, doing, done)
        # Tarefas pendentes (status = 'todo')
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE id_responsavel = %s AND status = "todo"', (usuario_id,))
        tarefas_pendentes = cursor.fetchone()['total']
        
        # Tarefas em andamento (status = 'doing')
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE id_responsavel = %s AND status = "doing"', (usuario_id,))
        tarefas_andamento = cursor.fetchone()['total']
        
        # Tarefas concluídas (status = 'done')
        cursor.execute('SELECT COUNT(*) as total FROM tarefas WHERE id_responsavel = %s AND status = "done"', (usuario_id,))
        tarefas_concluidas = cursor.fetchone()['total']
        
        # Dias ativo
        cursor.execute('SELECT data_cadastro FROM usuario WHERE id_usuario = %s', (usuario_id,))
        resultado = cursor.fetchone()
        
        dias_ativo = 0
        if resultado and resultado['data_cadastro']:
            from datetime import datetime
            data_cadastro = resultado['data_cadastro']
            if isinstance(data_cadastro, str):
                data_cadastro = datetime.strptime(data_cadastro, '%Y-%m-%d %H:%M:%S')
            dias_ativo = (datetime.now() - data_cadastro).days
        
        return jsonify({
            'total_tarefas': total_tarefas,
            'tarefas_pendentes': tarefas_pendentes,
            'tarefas_andamento': tarefas_andamento,
            'tarefas_concluidas': tarefas_concluidas,
            'dias_ativo': dias_ativo
        })
        
    except Exception as e:
        print(f"❌ Erro MySQL nas estatísticas do perfil: {e}")
        return jsonify({'error': 'Erro ao buscar estatísticas'}), 500
    finally:
        close_db_connection(connection)
        
@user.route('/api/perfil', methods=['PUT'])
def api_atualizar_perfil():
    """API para atualizar perfil do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    usuario_id = session['user_id']
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
                WHERE id_usuario = %s
            ''', (nome, email, senha_hash, usuario_id))
        else:
            # Se não, manter senha atual
            cursor.execute('''
                UPDATE usuario 
                SET nome = %s, email = %s
                WHERE id_usuario = %s
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