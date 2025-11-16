from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from database import conectar

bp_tabuleiro = Blueprint("tabuleiro", __name__, url_prefix="/tabuleiro")

def _nome_usuario_atual():
    nome = session.get("nome_usuario")
    if nome:
        return nome
    user_id = session.get("user_id")
    if not user_id:
        return "Jogador"
    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT nome FROM usuario WHERE id_usuario = %s", (user_id,))
        row = cur.fetchone()
        if not row:
            return "Jogador"
        if isinstance(row, dict):
            return row.get("nome") or "Jogador"
        return row[0] or "Jogador"
    except Exception:
        return "Jogador"
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()

def _verificar_acesso_projeto(id_projeto, user_id):
    """Verifica se o usuário tem acesso ao projeto (criador, administrador ou membro)"""
    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        
        # Verifica se é criador, administrador ou membro do projeto
        cur.execute("""
            SELECT 
                p.id_criador, 
                pm.id_usuario as eh_membro,
                pm.eh_administrador
            FROM projetos p
            LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto AND pm.id_usuario = %s
            WHERE p.id_projeto = %s
        """, (user_id, id_projeto))
        
        projeto = cur.fetchone()
        
        if not projeto:
            return False, False, False  # Projeto não existe
        
        eh_criador = projeto['id_criador'] == user_id
        eh_membro = projeto['eh_membro'] is not None
        eh_administrador = bool(projeto['eh_administrador'])  # Converte para boolean
        
        return eh_criador, eh_membro, eh_administrador
        
    except Exception as e:
        print(f"Erro ao verificar acesso: {e}")
        return False, False, False
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()

@bp_tabuleiro.route("/projeto/<int:id_projeto>", methods=["GET"])
def mostrar_tabuleiro_projeto(id_projeto):
    """Mostra o tabuleiro de um projeto específico"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_membro:
        flash("Acesso negado ao projeto", "danger")
        return redirect('/home')
    
    conn = cur = None
    recompensas = []
    progresso = None
    usuarios_online = []
    
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        
        # ✅ BUSCAR INFORMAÇÕES DO PROJETO - ESSENCIAL PARA O TEMPLATE
        cur.execute("""
            SELECT p.*, u.nome as criador_nome 
            FROM projetos p 
            JOIN usuario u ON p.id_criador = u.id_usuario 
            WHERE p.id_projeto = %s
        """, (id_projeto,))
        projeto = cur.fetchone()
        
        if not projeto:
            flash("Projeto não encontrado", "danger")
            return redirect('/home')
        
        # Buscar recompensas do projeto
        cur.execute("""
            SELECT * FROM recompensa 
            WHERE id_projeto = %s AND ativa = TRUE 
            ORDER BY posicao ASC
        """, (id_projeto,))
        recompensas = cur.fetchall()
        
        # Buscar progresso do usuário no tabuleiro
        cur.execute("""
            SELECT pt.posicao_atual, pt.saldo, t.total_casas
            FROM progresso_tabuleiro pt
            JOIN tabuleiro t ON pt.id_tabuleiro = t.id_tabuleiro
            WHERE t.id_projeto = %s AND pt.id_usuario = %s
        """, (id_projeto, user_id))
        progresso = cur.fetchone()
        
       # Buscar usuários online no projeto - VERSÃO DEFINITIVA
        cur.execute("""
            SELECT 
                u.id_usuario, 
                u.nome, 
                COALESCE(pt.posicao_atual, 1) as posicao_atual,
                COALESCE(pt.saldo, 0) as saldo
            FROM usuario u
            LEFT JOIN progresso_tabuleiro pt ON u.id_usuario = pt.id_usuario 
                AND pt.id_tabuleiro = (SELECT id_tabuleiro FROM tabuleiro WHERE id_projeto = %s)
            WHERE u.id_usuario IN (
                -- Membros que aceitaram convite DESTE projeto
                SELECT pm.id_usuario 
                FROM projeto_membros pm 
                WHERE pm.id_projeto = %s AND pm.data_aceitacao IS NOT NULL
                UNION 
                -- Criador DESTE projeto
                SELECT p.id_criador 
                FROM projetos p 
                WHERE p.id_projeto = %s
            )
            ORDER BY pt.posicao_atual DESC, u.nome ASC
        """, (id_projeto, id_projeto, id_projeto))
        usuarios_online = cur.fetchall()
        
        # Buscar recompensas conquistadas pelo usuário - ATUALIZADO PARA MOSTRAR DATA DE CONQUISTA
        cur.execute("""
            SELECT r.titulo, r.descricao, hr.data_conquista, r.posicao
            FROM historico_recompensas hr
            JOIN recompensa r ON hr.id_recompensa = r.id_recompensa
            WHERE hr.id_usuario = %s AND hr.id_projeto = %s
            ORDER BY hr.data_conquista DESC
        """, (user_id, id_projeto))
        recompensas_ganhas = cur.fetchall()
        
    except Exception as e:
        flash(f"Erro ao carregar tabuleiro: {e}", "danger")
        return redirect('/home')
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    
    # ✅ BUSCAR PRIMEIRO NOME DO USUÁRIO PARA O HEADER
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        cur.execute('SELECT nome FROM usuario WHERE id_usuario = %s', (session['user_id'],))
        usuario = cur.fetchone()
        primeiro_nome = usuario['nome'].split(' ')[0] if usuario and usuario['nome'] else 'Usuário'
    except Exception as e:
        print(f"Erro ao buscar nome do usuário: {e}")
        primeiro_nome = 'Usuário'
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    
    return render_template("tabuleiro.html",
                         projeto=projeto,  # ✅ VARIÁVEL ESSENCIAL
                         recompensas=recompensas,
                         progresso=progresso,
                         usuarios_online=usuarios_online,
                         recompensas_ganhas=recompensas_ganhas,
                         id_projeto=id_projeto,
                         eh_criador=eh_criador,
                         usuario_atual_eh_admin=eh_administrador,  # ✅ NOVA VARIÁVEL PARA ADMIN
                         primeiro_nome=primeiro_nome,  # ✅ PARA O HEADER
                         nome_usuario=_nome_usuario_atual())

@bp_tabuleiro.route("/projeto/<int:id_projeto>/adicionar_recompensa", methods=["POST"])
def adicionar_recompensa(id_projeto):
    """Adiciona recompensa ao tabuleiro do projeto - ATUALIZADO PARA BLOQUEAR CASA 1"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_administrador:
        flash("Apenas o criador ou administradores do projeto podem adicionar recompensas", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    posicao = (request.form.get("posicao") or "").strip()

    if not titulo or not posicao.isdigit():
        flash("Preencha título e uma posição válida.", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))
    
    # VALIDAÇÃO: Não permitir recompensa na casa 1
    posicao_int = int(posicao)
    if posicao_int == 1:
        flash("A casa 1 não pode ter recompensa. Por favor, escolha outra casa.", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recompensa (titulo, descricao, posicao, id_projeto) VALUES (%s,%s,%s,%s)",
            (titulo, descricao, posicao_int, id_projeto)
        )
        conn.commit()
        flash("Recompensa adicionada!", "success")
    except Exception as e:
        if conn: conn.rollback()
        flash(f"Erro ao adicionar recompensa: {e}", "danger")
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

@bp_tabuleiro.route("/projeto/<int:id_projeto>/editar_recompensa/<int:id_recompensa>", methods=["POST"])
def editar_recompensa(id_projeto, id_recompensa):
    """Edita recompensa do tabuleiro do projeto - ATUALIZADO PARA BLOQUEAR CASA 1"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_administrador:
        flash("Apenas o criador ou administradores do projeto podem editar recompensas", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    posicao = (request.form.get("posicao") or "").strip()

    if not titulo or not posicao.isdigit():
        flash("Preencha título e uma posição válida.", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))
    
    # VALIDAÇÃO: Não permitir recompensa na casa 1
    posicao_int = int(posicao)
    if posicao_int == 1:
        flash("A casa 1 não pode ter recompensa. Por favor, escolha outra casa.", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "UPDATE recompensa SET titulo=%s, descricao=%s, posicao=%s WHERE id_recompensa=%s AND id_projeto=%s",
            (titulo, descricao, posicao_int, id_recompensa, id_projeto)
        )
        conn.commit()
        flash("Recompensa atualizada!", "success")
    except Exception as e:
        if conn: conn.rollback()
        flash(f"Erro ao atualizar: {e}", "danger")
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

@bp_tabuleiro.route("/projeto/<int:id_projeto>/excluir/<int:id_recompensa>", methods=["POST"])
def excluir_recompensa(id_projeto, id_recompensa):
    """Exclui recompensa do tabuleiro do projeto"""
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_administrador:
        flash("Apenas o criador ou administradores do projeto podem excluir recompensas", "warning")
        return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM recompensa WHERE id_recompensa=%s AND id_projeto=%s", (id_recompensa, id_projeto))
        conn.commit()
        flash("Recompensa excluída!", "success")
    except Exception as e:
        if conn: conn.rollback()
        flash(f"Erro ao excluir: {e}", "danger")
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    return redirect(url_for('tabuleiro.mostrar_tabuleiro_projeto', id_projeto=id_projeto))

@bp_tabuleiro.route("/projeto/<int:id_projeto>/girar_dado", methods=["POST"])
def girar_dado(id_projeto):
    """Gira o dado e move o jogador no tabuleiro - ATUALIZADO PARA NÃO DAR BÔNUS DE SALDO"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_membro:
        return jsonify({'error': 'Acesso negado'}), 403

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        
        # Verificar saldo do usuário
        cur.execute("""
            SELECT pt.saldo, pt.posicao_atual, t.total_casas
            FROM progresso_tabuleiro pt
            JOIN tabuleiro t ON pt.id_tabuleiro = t.id_tabuleiro
            WHERE t.id_projeto = %s AND pt.id_usuario = %s
        """, (id_projeto, user_id))
        
        progresso = cur.fetchone()
        
        if not progresso or progresso['saldo'] <= 0:
            return jsonify({'error': 'Saldo insuficiente para girar o dado'}), 400
        
        # Girar dado (1-6)
        resultado_dado = __import__('random').randint(1, 6)
        
        # Calcular nova posição
        nova_posicao = progresso['posicao_atual'] + resultado_dado
        if nova_posicao > progresso['total_casas']:
            nova_posicao = progresso['total_casas']
        
        # Atualizar posição e saldo
        cur.execute("""
            UPDATE progresso_tabuleiro pt
            JOIN tabuleiro t ON pt.id_tabuleiro = t.id_tabuleiro
            SET pt.posicao_atual = %s, pt.saldo = pt.saldo - 1, pt.data_ultima_atualizacao = NOW()
            WHERE t.id_projeto = %s AND pt.id_usuario = %s
        """, (nova_posicao, id_projeto, user_id))
        
        # Verificar se caiu em recompensa APENAS NA POSIÇÃO FINAL
        cur.execute("""
            SELECT r.id_recompensa, r.titulo, r.descricao
            FROM recompensa r
            WHERE r.id_projeto = %s AND r.posicao = %s AND r.ativa = TRUE
        """, (id_projeto, nova_posicao))
        
        recompensa = cur.fetchone()
        
        if recompensa:
            # Verificar se o usuário já conquistou esta recompensa
            cur.execute("""
                SELECT id_historico FROM historico_recompensas 
                WHERE id_usuario = %s AND id_recompensa = %s AND id_projeto = %s
            """, (user_id, recompensa['id_recompensa'], id_projeto))
            
            recompensa_existente = cur.fetchone()
            
            if not recompensa_existente:
                # Registrar recompensa conquistada (SEM DAR SALDO EXTRA)
                cur.execute("""
                    INSERT INTO historico_recompensas (id_usuario, id_recompensa, id_projeto)
                    VALUES (%s, %s, %s)
                """, (user_id, recompensa['id_recompensa'], id_projeto))
            else:
                # Usuário já tem esta recompensa
                recompensa = None
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'resultado_dado': resultado_dado,
            'nova_posicao': nova_posicao,
            'recompensa': recompensa,
            'saldo_restante': progresso['saldo'] - 1  # REMOVIDO: + saldo_extra
        })
        
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'error': f'Erro ao girar dado: {e}'}), 500
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()

@bp_tabuleiro.route("/projeto/<int:id_projeto>/recomecar", methods=["POST"])
def recomecar_jogo(id_projeto):
    """Recomeça o jogo para o usuário atual - NOVA ROTA"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    user_id = session['user_id']
    eh_criador, eh_membro, eh_administrador = _verificar_acesso_projeto(id_projeto, user_id)
    
    if not eh_criador and not eh_membro:
        return jsonify({'error': 'Acesso negado'}), 403

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        
        # Resetar posição e saldo do usuário
        cur.execute("""
            UPDATE progresso_tabuleiro pt
            JOIN tabuleiro t ON pt.id_tabuleiro = t.id_tabuleiro
            SET pt.posicao_atual = 0, pt.saldo = 0, pt.data_ultima_atualizacao = NOW()
            WHERE t.id_projeto = %s AND pt.id_usuario = %s
        """, (id_projeto, user_id))
        
        # Remover recompensas conquistadas pelo usuário neste projeto
        cur.execute("""
            DELETE FROM historico_recompensas 
            WHERE id_usuario = %s AND id_projeto = %s
        """, (user_id, id_projeto))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'nova_posicao': 0,
            'novo_saldo': 0
        })
        
    except Exception as e:
        if conn: conn.rollback()
        return jsonify({'error': f'Erro ao recomeçar jogo: {e}'}), 500
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()

@bp_tabuleiro.route("/projeto/<int:id_projeto>/saldo", methods=["GET"])
def obter_saldo(id_projeto):
    """Obtém o saldo atual do usuário"""
    if 'user_id' not in session:
        return jsonify({'error': 'Não logado'}), 401
    
    user_id = session['user_id']
    
    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        
        cur.execute("""
            SELECT pt.saldo, pt.posicao_atual
            FROM progresso_tabuleiro pt
            JOIN tabuleiro t ON pt.id_tabuleiro = t.id_tabuleiro
            WHERE t.id_projeto = %s AND pt.id_usuario = %s
        """, (id_projeto, user_id))
        
        progresso = cur.fetchone()
        
        if not progresso:
            return jsonify({'saldo': 0, 'posicao_atual': 0})
        
        return jsonify({
            'saldo': progresso['saldo'],
            'posicao_atual': progresso['posicao_atual']
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao obter saldo: {e}'}), 500
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()

tabuleiro = bp_tabuleiro