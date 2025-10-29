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
        
        # CORREÇÃO: Consulta mais específica e usando colunas corretas
        cursor.execute('''
            SELECT 
                t.id_tarefa,
                t.titulo,
                t.descricao,
                t.prioridade,
                t.status,
                t.data_criacao,
                t.data_vencimento,  -- CORREÇÃO: usando data_vencimento em vez de prazo
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
        
        # Converter datetime para string para JSON (maneira mais segura)
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
    """API para atualizar uma tarefa"""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não logado'}), 401
    
    dados = request.get_json()
    if not dados:
        return jsonify({'error': 'Dados JSON inválidos'}), 400
    
    novo_status = dados.get('status')
    comentarios = dados.get('comentarios', '')
    
    connection = conectar()
    if not connection:
        return jsonify({'error': 'Erro de conexão com o banco'}), 500
    
    try:
        cursor = connection.cursor()
        
        # CORREÇÃO: Verificação mais completa de permissões
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
        
        # Atualizar tarefa
        cursor.execute('''
            UPDATE tarefas 
            SET status = %s, comentarios = %s
            WHERE id_tarefa = %s
        ''', (novo_status, comentarios, id_tarefa))
        
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
        
        print(f"✅ Tarefa '{titulo}' criada com sucesso no projeto {id_projeto}")
        return redirect(url_for('work.visualizar_projeto', id_projeto=id_projeto))
        
    except Exception as e:
        print(f"❌ Erro ao criar tarefa: {e}")
        return f"Erro interno ao criar tarefa: {e}", 500
    finally:
        close_db_connection(connection)
    

@task.route('/projeto/<int:id_projeto>/tarefa/<int:id_tarefa>/excluir', methods=['POST'])
def excluir_tarefa(id_projeto, id_tarefa):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    connection = None
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