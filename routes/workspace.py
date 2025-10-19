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
"""

 rota para página de um espaço específico

"""

@work.route('/projeto/<int:id>')
def visualizar_projeto(id_projeto):
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Buscar projeto
    cursor.execute("""
        SELECT p.*, u.nome as criador_nome 
        FROM projetos p 
        JOIN usuarios u ON p.id_criador = u.id_usuario 
        WHERE p.id_projeto = %s
    """, (id_projeto,))
    projeto = cursor.fetchone()
    
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
        JOIN usuarios u ON t.id_criador = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'todo'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_todo = cursor.fetchall()
    
    cursor.execute("SELECT * FROM tarefas WHERE id_projeto = %s AND status = 'doing'", (id_projeto,))
    tarefas_doing = cursor.fetchall()
    
    cursor.execute("SELECT * FROM tarefas WHERE id_projeto = %s AND status = 'done'", (id_projeto,))
    tarefas_done = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    eh_criador = projeto['id_criador'] == session['user_id']
    
    return render_template('projeto.html',
                         projeto=projeto,
                         tarefas_todo=tarefas_todo,
                         tarefas_doing=tarefas_doing,
                         tarefas_done=tarefas_done,
                         eh_criador=eh_criador)

"""

ROTA PARA CRIAR TAREFA 

"""

@work.route('/projeto/<int:id_projeto>/tarefa', methods=['POST'])
def criar_tarefa(id_projeto):
    if 'user_id' not in session:
        return redirect('/login')
    
    # Verificar se usuário é o criador do projeto
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
    projeto = cursor.fetchone()
    
    if projeto['id_criador'] != session['user_id']:
        return "Apenas o criador do projeto pode adicionar tarefas", 403
    
    titulo = request.form['titulo']
    descricao = request.form.get('descricao', '')
    prioridade = request.form.get('prioridade', 'media')
    data_vencimento = request.form.get('data_vencimento')
    
    cursor.execute("""
        INSERT INTO tarefas (titulo, descricao, prioridade, data_vencimento, id_projeto, id_criador)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (titulo, descricao, prioridade, data_vencimento, id_projeto, session['user_id']))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('work.visualizar_projeto', id_projeto=id_projeto))

#atualiza status
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
