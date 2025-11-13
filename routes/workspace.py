from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import conectar
from .email_service import EmailService, gerar_token_convite, calcular_expiracao
import os

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
    
    # Buscar projetos onde o usuário é criador OU membro (com convite aceito)
    cursor.execute("""
    SELECT DISTINCT p.*
    FROM projetos p
    LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto
    WHERE (p.id_criador = %s OR (pm.id_usuario = %s AND pm.data_aceitacao IS NOT NULL))
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
    
    # Verificar se usuário tem acesso ao projeto (criador OU membro com convite aceito)
    cursor.execute("""
        SELECT 1 FROM projeto_membros 
        WHERE id_projeto = %s AND id_usuario = %s AND data_aceitacao IS NOT NULL
        UNION
        SELECT 1 FROM projetos 
        WHERE id_projeto = %s AND id_criador = %s
    """, (id_projeto, session['user_id'], id_projeto, session['user_id']))
    
    if not cursor.fetchone():
        return "Acesso negado", 403
    
    # Buscar tarefas por status
    cursor.execute("""
        SELECT t.*, u.nome as responsavel_nome 
        FROM tarefas t 
        JOIN usuario u ON t.id_responsavel = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'todo'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_todo = cursor.fetchall()
    
    cursor.execute("""
        SELECT t.*, u.nome as responsavel_nome 
        FROM tarefas t 
        JOIN usuario u ON t.id_responsavel = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'doing'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_doing = cursor.fetchall()
    
    cursor.execute("""
        SELECT t.*, u.nome as responsavel_nome
        FROM tarefas t 
        JOIN usuario u ON t.id_responsavel = u.id_usuario 
        WHERE t.id_projeto = %s AND t.status = 'done'
        ORDER BY t.data_criacao DESC
    """, (id_projeto,))
    tarefas_done = cursor.fetchall()
    
    # Buscar membros do projeto (apenas os que aceitaram o convite) COM INFORMAÇÃO DE ADMIN
    cursor.execute("""
        SELECT u.id_usuario, u.nome, u.email, pm.eh_administrador
        FROM projeto_membros pm
        JOIN usuario u ON pm.id_usuario = u.id_usuario
        WHERE pm.id_projeto = %s AND pm.data_aceitacao IS NOT NULL
    """, (id_projeto,))
    membros = cursor.fetchall()
    
    # Buscar convites pendentes
    cursor.execute("""
        SELECT cp.*, u.nome, u.email
        FROM convite_projeto cp
        JOIN usuario u ON cp.id_usuario = u.id_usuario
        WHERE cp.id_projeto = %s AND cp.data_expiracao > NOW()
    """, (id_projeto,))
    convites_pendentes = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    eh_criador = projeto['id_criador'] == session['user_id']
    
    # Verificar se usuário atual é administrador (criador OU membro com flag admin)
    usuario_atual_eh_admin = eh_criador
    if not usuario_atual_eh_admin:
        for membro in membros:
            if membro['id_usuario'] == session['user_id'] and membro['eh_administrador']:
                usuario_atual_eh_admin = True
                break
    
    return render_template('projeto.html',
                         projeto=projeto,
                         tarefas_todo=tarefas_todo,
                         tarefas_doing=tarefas_doing,
                         tarefas_done=tarefas_done,
                         membros=membros,
                         convites_pendentes=convites_pendentes,
                         eh_criador=eh_criador,
                         usuario_atual_eh_admin=usuario_atual_eh_admin,  # NOVO PARÂMETRO
                         criador={'nome': projeto['criador_nome']})

@work.route('/projeto/<int:id_projeto>/membros', methods=['POST'])
def adicionar_membro(id_projeto):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Verificar se é o criador OU um administrador
    cursor.execute("""
        SELECT p.id_criador, pm.eh_administrador
        FROM projetos p
        LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto AND pm.id_usuario = %s
        WHERE p.id_projeto = %s
    """, (session['user_id'], id_projeto))
    
    projeto_info = cursor.fetchone()
    
    if not projeto_info or (projeto_info['id_criador'] != session['user_id'] and not projeto_info['eh_administrador']):
        return jsonify({'error': 'Apenas o criador ou administradores podem adicionar membros'}), 403
    
    email_membro = request.json.get('email')
    
    if not email_membro:
        return jsonify({'error': 'Email é obrigatório'}), 400
    
    # Buscar usuário pelo email
    cursor.execute("SELECT id_usuario, nome FROM usuario WHERE email = %s", (email_membro,))
    usuario = cursor.fetchone()
    
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    # Verificar se já é membro (aceito)
    cursor.execute("""
        SELECT 1 FROM projeto_membros 
        WHERE id_projeto = %s AND id_usuario = %s AND data_aceitacao IS NOT NULL
    """, (id_projeto, usuario['id_usuario']))
    
    if cursor.fetchone():
        return jsonify({'error': 'Usuário já é membro do projeto'}), 400
    
    # Verificar se já existe convite pendente
    cursor.execute("""
        SELECT 1 FROM convite_projeto 
        WHERE id_projeto = %s AND id_usuario = %s AND data_expiracao > NOW()
    """, (id_projeto, usuario['id_usuario']))
    
    if cursor.fetchone():
        return jsonify({'error': 'Já existe um convite pendente para este usuário'}), 400
    
    # Gerar token e data de expiração
    token = gerar_token_convite()
    data_expiracao = calcular_expiracao()
    
    # Criar convite
    cursor.execute("""
        INSERT INTO convite_projeto (id_projeto, id_usuario, token, data_expiracao, id_convidante)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_projeto, usuario['id_usuario'], token, data_expiracao, session['user_id']))
    
    # Buscar informações para o email
    cursor.execute("SELECT nome FROM projetos WHERE id_projeto = %s", (id_projeto,))
    projeto_info = cursor.fetchone()
    
    cursor.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (session['user_id'],))
    convidante_info = cursor.fetchone()
    
    connection.commit()
    cursor.close()
    connection.close()
    
    # Enviar email de convite
    email_service = EmailService()
    email_enviado = email_service.enviar_convite_projeto(
        email_membro,
        usuario['nome'],
        projeto_info['nome'],
        convidante_info['nome'],
        token
    )
    
    if email_enviado:
        return jsonify({
            'success': True, 
            'message': 'Convite enviado com sucesso! O usuário receberá um email para aceitar o convite.'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Convite criado, mas houve um erro ao enviar o email. O usuário pode aceitar pelo link posteriormente.'
        })

@work.route('/projeto/<int:id_projeto>/tarefa/<int:id_tarefa>/status', methods=['POST'])
def atualizar_status_tarefa(id_projeto, id_tarefa):
    novo_status = request.json['status']
    
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Buscar dados atuais da tarefa
        cursor.execute("SELECT * FROM tarefas WHERE id_tarefa = %s", (id_tarefa,))
        tarefa = cursor.fetchone()
        
        # Atualizar status
        cursor.execute("UPDATE tarefas SET status = %s WHERE id_tarefa = %s", (novo_status, id_tarefa))
        
        # Se a tarefa foi concluída e ainda não gerou saldo
        if (novo_status == 'done' and tarefa['status'] != 'done' and 
            not tarefa['saldo_gerado'] and tarefa['id_responsavel']):
            
            # Buscar tabuleiro do projeto
            cursor.execute("SELECT id_tabuleiro FROM tabuleiro WHERE id_projeto = %s", (id_projeto,))
            tabuleiro = cursor.fetchone()
            
            if tabuleiro:
                # Atualizar saldo do usuário
                cursor.execute("""
                    INSERT INTO progresso_tabuleiro (id_usuario, id_tabuleiro, saldo, posicao_atual)
                    VALUES (%s, %s, 1, 0)
                    ON DUPLICATE KEY UPDATE 
                        saldo = saldo + 1,
                        data_ultima_atualizacao = NOW()
                """, (tarefa['id_responsavel'], tabuleiro['id_tabuleiro']))
                
                # Registrar no histórico
                cursor.execute("""
                    INSERT INTO historico_saldo (id_usuario, id_tarefa, id_projeto, saldo_gerado)
                    VALUES (%s, %s, %s, 1)
                """, (tarefa['id_responsavel'], id_tarefa, id_projeto))
                
                # Marcar como saldo gerado
                cursor.execute("UPDATE tarefas SET saldo_gerado = TRUE WHERE id_tarefa = %s", (id_tarefa,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        connection.rollback()
        cursor.close()
        connection.close()
        print(f"❌ Erro ao atualizar status da tarefa: {e}")
        return jsonify({'error': 'Erro interno ao atualizar tarefa'}), 500

@work.route('/projeto/<int:id_projeto>/membros/<int:id_usuario>/remover', methods=['POST'])
def remover_membro(id_projeto, id_usuario):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se é o criador do projeto OU administrador
        cursor.execute("""
            SELECT p.id_criador, pm.eh_administrador
            FROM projetos p
            LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto AND pm.id_usuario = %s
            WHERE p.id_projeto = %s
        """, (session['user_id'], id_projeto))
        
        projeto_info = cursor.fetchone()
        
        if not projeto_info or (projeto_info['id_criador'] != session['user_id'] and not projeto_info['eh_administrador']):
            return jsonify({'error': 'Apenas o criador ou administradores podem remover membros'}), 403
        
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

@work.route('/projeto/<int:id_projeto>/sair', methods=['POST'])
def sair_do_projeto(id_projeto):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se o usuário é membro do projeto
        cursor.execute("""
            SELECT id_criador FROM projetos WHERE id_projeto = %s
        """, (id_projeto,))
        projeto = cursor.fetchone()
        
        if not projeto:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Se for o criador, não pode sair (precisa excluir o projeto ou transferir)
        if projeto['id_criador'] == session['user_id']:
            return jsonify({'error': 'O criador não pode sair do projeto. Exclua o projeto ou transfira a criação.'}), 400
        
        # Verificar se é membro
        cursor.execute("""
            SELECT 1 FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s AND data_aceitacao IS NOT NULL
        """, (id_projeto, session['user_id']))
        
        if not cursor.fetchone():
            return jsonify({'error': 'Você não é membro deste projeto'}), 400
        
        # Remover membro
        cursor.execute("""
            DELETE FROM projeto_membros 
            WHERE id_projeto = %s AND id_usuario = %s
        """, (id_projeto, session['user_id']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return redirect('/home')
        
    except Exception as e:
        print(f"❌ Erro ao sair do projeto: {e}")
        return jsonify({'error': 'Erro interno'}), 500

# ====================================
# NOVAS ROTAS PARA GERENCIAR PERMISSÕES DE ADMINISTRADOR
# ====================================

@work.route('/projeto/<int:id_projeto>/membros/<int:id_usuario>/tornar-admin', methods=['POST'])
def tornar_administrador(id_projeto, id_usuario):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se é o criador do projeto
        cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
        projeto = cursor.fetchone()
        
        if projeto['id_criador'] != session['user_id']:
            return jsonify({'error': 'Apenas o criador pode alterar permissões'}), 403
        
        # Tornar membro administrador
        cursor.execute("""
            UPDATE projeto_membros 
            SET eh_administrador = TRUE 
            WHERE id_projeto = %s AND id_usuario = %s
        """, (id_projeto, id_usuario))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Usuário agora é administrador'})
        
    except Exception as e:
        print(f"❌ Erro ao tornar administrador: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@work.route('/projeto/<int:id_projeto>/membros/<int:id_usuario>/rebaixar', methods=['POST'])
def rebaixar_membro(id_projeto, id_usuario):
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se é o criador do projeto
        cursor.execute("SELECT id_criador FROM projetos WHERE id_projeto = %s", (id_projeto,))
        projeto = cursor.fetchone()
        
        if projeto['id_criador'] != session['user_id']:
            return jsonify({'error': 'Apenas o criador pode alterar permissões'}), 403
        
        # Não permitir rebaixar a si mesmo
        if id_usuario == session['user_id']:
            return jsonify({'error': 'Não é possível rebaixar a si mesmo'}), 400
        
        # Rebaixar administrador para membro normal
        cursor.execute("""
            UPDATE projeto_membros 
            SET eh_administrador = FALSE 
            WHERE id_projeto = %s AND id_usuario = %s
        """, (id_projeto, id_usuario))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Usuário rebaixado para membro'})
        
    except Exception as e:
        print(f"❌ Erro ao rebaixar membro: {e}")
        return jsonify({'error': 'Erro interno'}), 500

# ====================================
# ROTAS PARA SISTEMA DE CONVITES
# ====================================

@work.route('/convite/aceitar/<token>')
def aceitar_convite(token):
    """Página para aceitar convite de projeto"""
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Buscar convite válido
    cursor.execute("""
        SELECT cp.*, p.nome as projeto_nome, u.nome as usuario_nome, 
               uc.nome as convidante_nome
        FROM convite_projeto cp
        JOIN projetos p ON cp.id_projeto = p.id_projeto
        JOIN usuario u ON cp.id_usuario = u.id_usuario
        JOIN usuario uc ON cp.id_convidante = uc.id_usuario
        WHERE cp.token = %s AND cp.data_expiracao > NOW()
    """, (token,))
    
    convite = cursor.fetchone()
    
    if not convite:
        cursor.close()
        connection.close()
        return render_template('convite_expirado.html')
    
    cursor.close()
    connection.close()
    
    return render_template('aceitar_convite.html', convite=convite)

@work.route('/convite/aceitar/<token>/confirmar', methods=['POST'])
def confirmar_aceitacao_convite(token):
    """Confirma a aceitação do convite"""
    connection = conectar()
    cursor = connection.cursor(dictionary=True)
    
    # Verificar convite válido
    cursor.execute("""
        SELECT * FROM convite_projeto 
        WHERE token = %s AND data_expiracao > NOW()
    """, (token,))
    
    convite = cursor.fetchone()
    
    if not convite:
        cursor.close()
        connection.close()
        return jsonify({'error': 'Convite inválido ou expirado'}), 400
    
    try:
        # Adicionar como membro do projeto
        cursor.execute("""
            INSERT INTO projeto_membros (id_projeto, id_usuario, data_aceitacao)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE data_aceitacao = NOW()
        """, (convite['id_projeto'], convite['id_usuario']))
        
        # Remover convite
        cursor.execute("DELETE FROM convite_projeto WHERE token = %s", (token,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Convite aceito com sucesso! Agora você é membro do projeto.',
            'projeto_id': convite['id_projeto']
        })
        
    except Exception as e:
        print(f"❌ Erro ao aceitar convite: {e}")
        connection.rollback()
        cursor.close()
        connection.close()
        return jsonify({'error': 'Erro ao processar convite'}), 500

@work.route('/projeto/<int:id_projeto>/convite/<int:id_convite>/cancelar', methods=['POST'])
def cancelar_convite(id_projeto, id_convite):
    """Cancela um convite pendente"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    try:
        connection = conectar()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se é o criador do projeto OU administrador
        cursor.execute("""
            SELECT p.id_criador, pm.eh_administrador
            FROM projetos p
            LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto AND pm.id_usuario = %s
            WHERE p.id_projeto = %s
        """, (session['user_id'], id_projeto))
        
        projeto_info = cursor.fetchone()
        
        if not projeto_info or (projeto_info['id_criador'] != session['user_id'] and not projeto_info['eh_administrador']):
            return jsonify({'error': 'Apenas o criador ou administradores podem cancelar convites'}), 403
        
        # Cancelar convite
        cursor.execute("DELETE FROM convite_projeto WHERE id_convite = %s", (id_convite,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Convite cancelado com sucesso!'})
        
    except Exception as e:
        print(f"❌ Erro ao cancelar convite: {e}")
        return jsonify({'error': 'Erro interno'}), 500