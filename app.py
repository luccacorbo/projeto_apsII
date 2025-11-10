from flask import Flask, render_template, session
from routes.auth import auth
from routes.home import home
from routes.workspace import work
from routes.task import task
from routes.user import user
from routes.tabuleiro import tabuleiro as tabuleiro_bp
from database import conectar

app = Flask(__name__)
app.secret_key = "chave_secreta"

# Blueprints
app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(work)
app.register_blueprint(task)
app.register_blueprint(user)
app.register_blueprint(tabuleiro_bp)

# Deixa variáveis da sessão disponíveis nos templates
@app.context_processor
def inject_user():
    user_data = {}
    if 'user_id' in session:
        user_data = {
            'user_id': session.get('user_id'),
            'user_name': session.get('user_name'),
            'usuario_nome': session.get('usuario_nome'),
        }
    # injeta as chaves no escopo global do Jinja
    return dict(**user_data)

@app.route("/")
def inicio():
    nome = session.get("usuario_nome")
    return render_template("inicio.html", nome_usuario=nome)

if __name__ == "__main__":
    app.run(debug=True)
