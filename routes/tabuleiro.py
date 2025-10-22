from flask import Blueprint, render_template, request, redirect, jsonify
from database import conectar

bp_tabuleiro = Blueprint("tabuleiro", __name__, url_prefix="/tabuleiro")

# ===============================
# Mostrar tabuleiro com recompensas
# ===============================
@bp_tabuleiro.route("/", methods=["GET"])
def mostrar_tabuleiro():
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM recompensa ORDER BY posicao ASC")
    recompensas = cur.fetchall()
    conn.close()
    return render_template("tabuleiro.html", recompensas=recompensas)

# ===============================
# Adicionar recompensa
# ===============================
@bp_tabuleiro.route("/adicionar_recompensa", methods=["POST"])
def adicionar_recompensa():
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    posicao = request.form.get("posicao")

    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO recompensa (titulo, descricao, posicao) VALUES (%s, %s, %s)",
        (titulo, descricao, posicao)
    )
    conn.commit()
    conn.close()

    # 🔧 Aqui troquei o JSON por redirecionamento pro tabuleiro
    return redirect("/tabuleiro")

# ===============================
# Editar recompensa
# ===============================
@bp_tabuleiro.route("/editar_recompensa/<int:id_recompensa>", methods=["POST"])
def editar_recompensa(id_recompensa):
    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")
    posicao = request.form.get("posicao")

    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "UPDATE recompensa SET titulo=%s, descricao=%s, posicao=%s WHERE id_recompensa=%s",
        (titulo, descricao, posicao, id_recompensa)
    )
    conn.commit()
    conn.close()
    return redirect("/tabuleiro")

# ===============================
# Excluir recompensa
# ===============================
@bp_tabuleiro.route("/excluir/<int:id_recompensa>", methods=["POST"])
def excluir_recompensa(id_recompensa):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM recompensa WHERE id_recompensa=%s", (id_recompensa,))
    conn.commit()
    conn.close()
    return redirect("/tabuleiro")

# ===============================
# Registrar blueprint
# ===============================
tabuleiro = bp_tabuleiro