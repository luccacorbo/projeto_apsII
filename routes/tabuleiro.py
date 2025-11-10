from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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

@bp_tabuleiro.route("/", methods=["GET"])
def mostrar_tabuleiro():
    conn = cur = None
    recompensas = []
    try:
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM recompensa ORDER BY posicao ASC")
        recompensas = cur.fetchall()
    finally:
        try:
            if cur: cur.close()
        finally:
            if conn: conn.close()
    return render_template("tabuleiro.html",
                           recompensas=recompensas,
                           nome_usuario=_nome_usuario_atual())

@bp_tabuleiro.route("/adicionar_recompensa", methods=["POST"])
def adicionar_recompensa():
    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    posicao = (request.form.get("posicao") or "").strip()

    if not titulo or not posicao.isdigit():
        flash("Preencha título e uma posição válida.", "warning")
        return redirect(url_for("tabuleiro.mostrar_tabuleiro"))

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO recompensa (titulo, descricao, posicao) VALUES (%s,%s,%s)",
            (titulo, descricao, int(posicao))
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
    return redirect(url_for("tabuleiro.mostrar_tabuleiro"))

@bp_tabuleiro.route("/editar_recompensa/<int:id_recompensa>", methods=["POST"])
def editar_recompensa(id_recompensa):
    titulo = (request.form.get("titulo") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    posicao = (request.form.get("posicao") or "").strip()

    if not titulo or not posicao.isdigit():
        flash("Preencha título e uma posição válida.", "warning")
        return redirect(url_for("tabuleiro.mostrar_tabuleiro"))

    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute(
            "UPDATE recompensa SET titulo=%s, descricao=%s, posicao=%s WHERE id_recompensa=%s",
            (titulo, descricao, int(posicao), id_recompensa)
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
    return redirect(url_for("tabuleiro.mostrar_tabuleiro"))

@bp_tabuleiro.route("/excluir/<int:id_recompensa>", methods=["POST"])
def excluir_recompensa(id_recompensa):
    conn = cur = None
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM recompensa WHERE id_recompensa=%s", (id_recompensa,))
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
    return redirect(url_for("tabuleiro.mostrar_tabuleiro"))

# **Exporta com o nome que seu app.py espera**
tabuleiro = bp_tabuleiro
