from flask import Flask, session
from routes.auth import auth
from routes.home import home
from routes.workspace import work
from routes.task import task
from routes.user import user
from routes.tabuleiro import tabuleiro
from database import conectar

app = Flask(__name__)
app.secret_key = "chave_secreta"

# registra o blueprint de autenticação
app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(work)
app.register_blueprint(task)
app.register_blueprint(user)
app.register_blueprint(tabuleiro)


@app.context_processor
def inject_user():
    user_data = {}
    if 'user_id' in session:
        user_data = {
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name'),
            'usuario_nome': session.get('usuario_nome')
        }
    return user_data


@app.route('/')
def inicio():
    return render_template('inicio.html', nome_usuario=nome_usuario)

@app.route('/tabuleiro')
def tabuleiro():
    return render_template('tabuleiro.html')

if __name__ == "__main__":
    app.run(debug=True)
