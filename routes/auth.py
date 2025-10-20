# auth.py - COM DEBUG
from flask import Blueprint, render_template, request, session, redirect
from database import conectar, close_db_connection, hash_password, check_password

auth = Blueprint('auth', __name__)

@auth.route("/")
def index():
    return redirect('/login')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        print(f"🔍 DEBUG LOGIN - Email: {email}, Senha: {senha}")
        
        if not email or not senha:
            return render_template('login.html', error='Preencha todos os campos')
        
        connection = conectar()
        print(f"🔍 DEBUG - Conexão: {connection}")
        
        if not connection:
            return render_template('login.html', error='Erro de conexão com o banco')
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT id_usuario, nome, email, senha FROM usuario WHERE email = %s', (email,))
            usuario = cursor.fetchone()
            
            print(f"🔍 DEBUG - Usuário encontrado: {usuario}")
            
            if usuario:
                print(f"🔍 DEBUG - Senha do banco: {usuario['senha']}")
                print(f"🔍 DEBUG - Verificando senha...")
                senha_valida = check_password(usuario['senha'], senha)
                print(f"🔍 DEBUG - Senha válida: {senha_valida}")
            
            if usuario and check_password(usuario['senha'], senha):
                session['user_id'] = usuario['id_usuario']
                session['user_name'] = usuario['nome']
                print("✅ Login bem-sucedido!")
                return redirect('/home')
            else:
                print("❌ Email ou senha incorretos")
                return render_template('login.html', error='Email ou senha incorretos')
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return render_template('login.html', error='Erro ao fazer login')
        finally:
            close_db_connection(connection)
    
    return render_template('login.html')

@auth.route('/cadastro', methods=['GET', 'POST'])
@auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar', '')

        print(f"🔍 DEBUG CADASTRO - Iniciando cadastro...")
        print(f"🔍 DEBUG CADASTRO - Nome: '{nome}'")
        print(f"🔍 DEBUG CADASTRO - Email: '{email}'")
        print(f"🔍 DEBUG CADASTRO - Senha: '{senha}'")
        print(f"🔍 DEBUG CADASTRO - Confirmar Senha: '{confirmar}'")
        
        # Validações
        if not all([nome, email, senha, confirmar]):
            print("❌ DEBUG CADASTRO - Campos obrigatórios faltando")
            return render_template('cadastro.html', error='Todos os campos são obrigatórios')
        
        if senha != confirmar:
            print("❌ DEBUG CADASTRO - Senhas não coincidem")
            return render_template('cadastro.html', error='As senhas não coincidem')
        
        if len(senha) < 6:
            print("❌ DEBUG CADASTRO - Senha muito curta")
            return render_template('cadastro.html', error='A senha deve ter pelo menos 6 caracteres')
        
        connection = conectar()
        print(f"🔍 DEBUG CADASTRO - Conexão: {connection}")
        
        if not connection:
            print("❌ DEBUG CADASTRO - Sem conexão com banco")
            return render_template('cadastro.html', error='Erro de conexão com o banco')
        
        try:
            cursor = connection.cursor()
            senha_hash = hash_password(senha)
            print(f"🔍 DEBUG CADASTRO - Hash gerado: {senha_hash}")
            
            print(f"🔍 DEBUG CADASTRO - Executando INSERT...")
            cursor.execute(
                'INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)',
                (nome, email, senha_hash)
            )
            print(f"🔍 DEBUG CADASTRO - INSERT executado")
            
            connection.commit()
            print("✅ DEBUG CADASTRO - Commit realizado!")
            
            # Verificar se realmente foi inserido
            cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
            usuario_verificado = cursor.fetchone()
            print(f"🔍 DEBUG CADASTRO - Usuário verificado após insert: {usuario_verificado}")
            
            if usuario_verificado:
                print("🎉 DEBUG CADASTRO - USUÁRIO SALVO COM SUCESSO!")
            else:
                print("❌ DEBUG CADASTRO - USUÁRIO NÃO FOI SALVO!")
            
            return redirect('/login?cadastro=success')
            
        except Exception as e:
            print(f"❌ ERRO NO CADASTRO: {e}")
            print(f"❌ TIPO DO ERRO: {type(e)}")
            connection.rollback()
            if "Duplicate entry" in str(e) or "1062" in str(e):
                return render_template('cadastro.html', error='Email já está em uso')
            return render_template('cadastro.html', error=f'Erro ao criar conta: {str(e)}')
        finally:
            close_db_connection(connection)
        print("🔍 DEBUG CADASTRO - Fim do processo de cadastro")
    
    return render_template('cadastro.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/login')