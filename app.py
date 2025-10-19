from flask import Flask
from routes.auth import auth
from routes.home import home
from routes.workspace import work
from database import conectar

app = Flask(__name__)
app.secret_key = "chave_secreta"

# registra o blueprint de autenticação
app.register_blueprint(auth)
app.register_blueprint(home)
app.register_blueprint(work)

if __name__ == "__main__":
    app.run(debug=True)

@app.context_processor
def inject_projetos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projeto")
    projeto = cursor.fetchall()
    cursor.close()
    conn.close()
    return dict(projeto=projeto)
