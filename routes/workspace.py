from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import conectar

work = Blueprint('work', __name__)

@work.route('/criar-projeto', methods=['GET', 'POST'])
def criar_projeto():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        try:
            nome_projeto = request.form.get('nome_projeto', '').strip()
            
            if not nome_projeto:
                return "Nome do projeto é obrigatório", 400
            
            descricao_projeto = request.form.get('descricao_projeto', '').strip()
            
            print(f"📝 Tentando criar projeto: {nome_projeto}")
            
            connection = conectar()
            if not connection:
                return "Erro de conexão com o banco", 500
                
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO projetos (nome, descricao, id_criador) VALUES (%s, %s, %s)",
                (nome_projeto, descricao_projeto, session['user_id'])
            )
            connection.commit()
            cursor.close()
            connection.close()
            
            print("✅ Projeto criado com sucesso!")
            return redirect('/home')
            
        except KeyError as e:
            print(f"❌ Campo faltando no formulário: {e}")
            return f"Campo obrigatório faltando: {e}", 400
        except Exception as e:
            print(f"❌ Erro ao criar projeto: {e}")
            return f"Erro interno: {e}", 500
    
    # GET request - mostrar o formulário
    return render_template('criar-projeto.html')

# Nova rota para buscar projetos do usuário
@work.route('/api/meus-projetos')
def api_meus_projetos():
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Buscar projetos onde o usuário é criador OU membro
    cursor.execute("""
    SELECT DISTINCT p.*
    FROM projetos p
    LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto
    WHERE p.id_criador = %s OR pm.id_usuario = %s
    ORDER BY p.data_criacao DESC
""", (session['user_id'], session['user_id']))

    
    projetos = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Converter datas para string
    for projeto in projetos:
        if projeto['data_criacao']:
            projeto['data_criacao'] = projeto['data_criacao'].strftime('%d/%m/%Y')
    
    return jsonify(projetos)

@work.route('/projeto/<int:id_projeto>')
def visualizar_projeto(id_projeto):
    if 'user_id' not in session:
        return redirect('/login')
        
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Buscar projeto
    cursor.execute("""
        SELECT p.*, u.nome as criador_nome 
        FROM projetos p 
        JOIN usuario u ON p.id_criador = u.id_usuario 
        WHERE p.id_projeto = %s
    """, (id_projeto,))
    projeto = cursor.fetchone()
    
    if not projeto:
        return "Projeto não encontrado", 404
    
    # Verificar se usuário é membro do projeto
    cursor.execute("""
        SELECT 1 FROM projeto_membros 
        WHERE id_projeto = %s AND id_usuario = %s
        UNION
        SELECT 1 FROM projetos 
        WHERE id_projeto = %s AND id_criador = %s
    """, (id_projeto, session['user_id'], id_projeto, session['user_id']))
    
    if not cursor.fetchone():
        return "Acesso negado", 403
    
    # Buscar tarefas por status
    cursor.execute("""
        SELECT t.*, u.nome as criador_nome 
        FROM tarefas t 
        JOIN usuario u ON t.id_criador = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'todo'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_todo = cursor.fetchall()
    
    cursor.execute("""
        SELECT t.*, u.nome as criador_nome 
        FROM tarefas t 
        JOIN usuario u ON t.id_criador = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'doing'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_doing = cursor.fetchall()
    
    cursor.execute("""
        SELECT t.*, u.nome as criador_nome 
        FROM tarefas t 
        JOIN usuario u ON t.id_criador = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'done'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_done = cursor.fetchall()
    
    # Buscar membros do projeto
    cursor.execute("""
        SELECT u.id_usuario, u.nome, u.email
        FROM projeto_membros pm
        JOIN usuario u ON pm.id_usuario = u.id_usuario
        WHERE pm.id_projeto = %s
    """, (id_projeto,))
    membros = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    # CORREÇÃO AQUI: usar 'eh_criador' em vez de 'id_criador'
    eh_criador = projeto['id_criador'] == session['user_id']
    
    return render_template('projeto.html',
                         projeto=projeto,
                         tarefas_todo=tarefas_todo,
                         tarefas_doing=tarefas_doing,
                         tarefas_done=tarefas_done,
                         membros=membros,
                         eh_criador=eh_criador,  # ← Nome correto da variável
                         criador={'nome': projeto['criador_nome']})  # ← Criar objeto criador

# Nova rota para adicionar membros
@work.route('/projeto/<int:id_projeto>/membros', methods=['POST'])
def adicionar_membro(id_projeto):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    # Verificar se é o criador
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
    projeto = cursor.fetchone()
    
    if projeto['id_criador'] != session['user_id']:
        return jsonify({'error': 'Apenas o criador pode adicionar membros'}), 403
    
    email_membro = request.json.get('email')
    
    if not email_membro:
        return jsonify({'error': 'Email é obrigatório'}), 400
    
    # Buscar usuário pelo email
    cursor.execute("SELECT id_usuario, nome FROM usuario WHERE email = %s", (email_membro,))
    usuario = cursor.fetchone()
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Verificar se já é membro
    cursor.execute("SELECT 1 FROM projeto_membros WHERE id_projeto = %s AND id_usuario = %s", 
                   (id_projeto, usuario['id_usuario']))
    if cursor.fetchone():
        return jsonify({'error': 'Usuário já é membro do projeto'}), 400
    
    # Adicionar como membro
    cursor.execute("INSERT INTO projeto_membros (id_projeto, id_usuario) VALUES (%s, %s)", 
                   (id_projeto, usuario['id_usuario']))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'success': True, 'membro': {'nome': usuario['nome'], 'email': email_membro}})

@work.route('/projeto/<int:id_projeto>/tarefa/<int:id_tarefa>/status', methods=['POST'])
def atualizar_status_tarefa(id_projeto, id_tarefa):
    novo_status = request.json['status']
    
    connection = conectar()
    cursor = connection.cursor()
    cursor.execute("UPDATE tarefas SET status = %s WHERE id_tarefa = %s", (novo_status, id_tarefa))
    connection.commit()
    cursor.close()
    connection.close()
    
    return jsonify({'success': True})

@work.route('/projeto/<int:id_projeto>/membros/<int:id_usuario>/remover', methods=['POST'])
def remover_membro(id_projeto, id_usuario):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se é o criador do projeto
        cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
        projeto = cursor.fetchone()
        
        if projeto['id_criador'] != session['user_id']:
            return jsonify({'error': 'Apenas o criador pode remover membros'}), 403
        
        # Não permitir remover a si mesmo
        if id_usuario == session['user_id']:
            return jsonify({'error': 'Não é possível remover a si mesmo'}), 400
        
        # Remover membro
        cursor.execute("DELETE FROM projeto_membros WHERE id_projeto = %s AND id_usuario = %s", 
                      (id_projeto, id_usuario))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"❌ Erro ao remover membro: {e}")
        return jsonify({'error': 'Erro interno'}), 500

#rota para excluir o projeto

@work.route('/projeto/<int:id_projeto>/excluir', methods=['POST'])
def excluir_projeto(id_projeto):
    if 'user_id' not in session:
        return redirect('/login')
    
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Verificar se é o criador
    cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
    projeto = cursor.fetchone()
    
    if projeto['id_criador'] != session['user_id']:
        return "Apenas o criador pode excluir o projeto", 403
    
    # Excluir projeto (as tarefas serão excluídas em cascata se as FK estiverem configuradas)
    cursor.execute("DELETE FROM projetos WHERE id_projeto = %s", (id_projeto,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect('/home')
