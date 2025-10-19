from flask import Blueprint, render_template, request, redirect, url_for
from database import conectar

work = Blueprint('work', __name__)

@work.route('/criar-projeto', methods=['GET', 'POST'])
def criar_projeto():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        titulo = request.form['titulo']
        cursor.execute("INSERT INTO projeto (titulo) VALUES (%s)", (titulo,))
        conn.commit()
        return redirect(url_for('home.retornaInicio'))

    # busca todos os espaços para exibir na lateral
    cursor.execute("SELECT * FROM projeto")
    projeto = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('criar-projeto.html', projeto=projeto)


# rota para página de um espaço específico
@work.route('/projeto/<int:id>')
def visualizar_projeto(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projeto WHERE id = %s", (id,))
    projeto = cursor.fetchone()
    cursor.close()
    conn.close()

    if not projeto:
        return "Projeto não encontrado", 404

    return render_template('projeto.html', projeto=projeto)
