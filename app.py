from flask import Flask
from routes.auth import auth
from routes.home import home

app = Flask(__name__)
app.secret_key = "chave_secreta"

# registra o blueprint de autenticação
app.register_blueprint(auth)
app.register_blueprint(home)

if __name__ == "__main__":
    app.run(debug=True)

