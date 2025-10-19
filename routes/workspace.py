from flask import Blueprint, render_template, request, redirect, url_for
from database import conectar

work = Blueprint('work', __name__)

@work.route('/criar-espaco', methods=['GET', 'POST'])
def criar_espaco():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        nome = request.form['nome']
        cursor.execute("INSERT INTO espacos (nome) VALUES (%s)", (nome,))
        conn.commit()
        return redirect(url_for('home.retornaInicio'))

    # busca todos os espaços para exibir na lateral
    cursor.execute("SELECT * FROM espacos")
    espacos = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('criar_espaco.html', espacos=espacos)


# rota para página de um espaço específico
@work.route('/espaco/<int:id>')
def visualizar_espaco(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM espacos WHERE id = %s", (id,))
    espaco = cursor.fetchone()
    cursor.close()
    conn.close()

    if not espaco:
        return "Espaço não encontrado", 404

    return render_template('espaco.html', espaco=espaco)
