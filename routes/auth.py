# auth.py
from flask import Blueprint, render_template, request, session, redirect, url_for
from database import conectar, close_db_connection, hash_password, check_password, generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route("/")
def home():
    return render_template("login.html")

#retorna para a pagina de login
@auth.route('/login')
def retonarlogin():
    return render_template('login.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        print(f"📧 Tentando login com: {email}")
        
        if not email or not senha:
            return render_template('login.html', error='Preencha todos os campos')
        
        connection = conectar()
        if not connection:
            return render_template('login.html', error='Erro de conexão com o banco')
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT id_usuario, nome, email, senha FROM usuario WHERE email = %s', (email,))
            usuario = cursor.fetchone()
            
            print(f"👤 Usuário encontrado: {usuario}")
            
            if usuario and check_password(usuario['senha'], senha):
                session['usuario_id'] = usuario['id_usuario']
                session['usuario_nome'] = usuario['nome']
                session['usuario_email'] = usuario['email']
                print("✅ Login bem-sucedido!")

                session['user_id'] = usuario['id_usuario']
                session['user_name'] = usuario['nome']
                session['nome_usuario'] = usuario['nome']

                return render_template('inicio.html')
            else:
                print("❌ Email ou senha incorretos")
                return render_template('login.html', error='Email ou senha incorretos')
                
        except Exception as e:
            print(f"❌ Erro MySQL: {e}")
            return render_template('login.html', error='Erro ao fazer login')
        finally:
            close_db_connection(connection)
    
    return render_template('login.html')

@auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
       
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')

        senha_hash = hash_password(senha)
        
        print(f"📝 Dados do cadastro: nome={nome}, email={email}")
        
        # Validação dos campos
        campos_obrigatorios = [
            ('nome', nome, 'Nome'),
            ('email', email, 'E-mail'),
            ('senha', senha, 'Senha'),
            ('confirmar_senha', confirmar_senha, 'Confirmação de senha')
        ]
        
        for campo_nome, campo_valor, campo_label in campos_obrigatorios:
            if not campo_valor:
                return render_template('cadastro.html', error=f'{campo_label} é obrigatório')
        
        if senha != confirmar_senha:
            return render_template('cadastro.html', error='As senhas não coincidem')
        
        if len(senha) < 6:
            return render_template('cadastro.html', error='A senha deve ter pelo menos 6 caracteres')
        
        if len(nome) < 2:
            return render_template('cadastro.html', error='Nome deve ter pelo menos 2 caracteres')
        
        connection = conectar()
        if not connection:
            return render_template('cadastro.html', error='Erro de conexão com o banco')
        
        try:
            cursor = connection.cursor()
            senha_hash = generate_password_hash(senha)
            
            cursor.execute(
                'INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)',
                (nome, email, senha_hash)
            )
            connection.commit()
            
            print(f"✅ Usuário {nome} cadastrado com sucesso!")
            
            # Redirecionar para login com mensagem de sucesso
            return redirect('/auth/login?cadastro=success')
            
        except Exception as e:
            print(f"❌ Erro MySQL: {e}")
            connection.rollback()
            
            if "Duplicate entry" in str(e) or "1062" in str(e):
                return render_template('cadastro.html', error='Email já está em uso')
            else:
                return render_template('cadastro.html', error='Erro ao criar conta')
        finally:
            close_db_connection(connection)
    
    return render_template('cadastro.html')

@auth.route('/logout')
def logout():
    session.clear()
    print("✅ Usuário deslogado")
    return redirect('/auth/login?logout=success')