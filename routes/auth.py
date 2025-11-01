from flask import Blueprint, render_template, request, session, redirect
from database import conectar, close_db_connection, hash_password, check_password
import secrets
from datetime import datetime, timedelta
from .email_service import EmailService  # NOVA IMPORTACAO

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
            # Novo: Verifica se a mensagem de sucesso (success) está na URL para exibir
            success_message = request.args.get('success')
            return render_template('login.html', error='Preencha todos os campos', success=success_message)
        
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
                # Novo: Verifica se a mensagem de sucesso (success) está na URL para exibir
                success_message = request.args.get('success')
                return render_template('login.html', error='Email ou senha incorretos', success=success_message)
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return render_template('login.html', error='Erro ao fazer login')
        finally:
            close_db_connection(connection)
    
    # Novo: Captura mensagens de erro e sucesso da URL para exibir
    error_message = request.args.get('error')
    success_message = request.args.get('success')
    return render_template('login.html', error=error_message, success=success_message)

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

# ====================================================
# ROTAS DE RECUPERAÇÃO DE SENHA (ATUALIZADAS COM EMAIL REAL)
# ====================================================

# ----------------------------------------------------
# Rota 1: Formulário de solicitação de redefinição
# ----------------------------------------------------
@auth.route('/esqueci-minha-senha')
def esqueci_minha_senha():
    # Novo: Captura mensagens de erro e sucesso da URL para exibir
    error_message = request.args.get('error')
    success_message = request.args.get('success')
    return render_template('esqueci_senha.html', error=error_message, success=success_message)

# ----------------------------------------------------
# Rota 2: Gerar Token e Enviar E-mail Real
# ----------------------------------------------------
@auth.route('/enviar-reset-link', methods=['POST'])
def enviar_reset_link():
    email = request.form.get('email', '').strip()
    
    connection = conectar()
    if not connection:
        return redirect('/esqueci-minha-senha?error=Houve um erro no sistema. Tente novamente.')

    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Buscar o usuário pelo e-mail
        cursor.execute('SELECT id_usuario, nome, email FROM usuario WHERE email = %s', (email,))
        usuario = cursor.fetchone()
        
        # 2. Segurança: MENSAGEM GENÉRICA, independente de o e-mail existir ou não
        mensagem_sucesso = 'Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha.'
        
        if not usuario:
            print(f"🔍 DEBUG - E-mail '{email}' não encontrado, mas a mensagem de sucesso será exibida por segurança.")
            return redirect(f'/esqueci-minha-senha?success={mensagem_sucesso}')

        user_id = usuario['id_usuario']
        nome_usuario = usuario['nome']
        email_usuario = usuario['email']
        
        # 3. Gerar Token e Expiração
        token = secrets.token_urlsafe(32)
        # Token expira em 1 hora
        expires_at = datetime.now() + timedelta(hours=1)
        
        # 4. Salvar Token no DB (Limpar tokens antigos do mesmo usuário primeiro)
        # Limpa tokens antigos
        cursor.execute('DELETE FROM recuperacao_senha WHERE user_id = %s', (user_id,))
        # Insere o novo token
        cursor.execute(
            'INSERT INTO recuperacao_senha (user_id, token, expires_at) VALUES (%s, %s, %s)',
            (user_id, token, expires_at)
        )
        connection.commit()
        
        # 5. ENVIAR E-MAIL REAL (substituindo a simulação)
        email_service = EmailService()
        email_enviado = email_service.enviar_redefinicao_senha(
            email_usuario, 
            nome_usuario, 
            token
        )
        
        if email_enviado:
            print(f"✅ Email de redefinição enviado com sucesso para: {email_usuario}")
        else:
            print(f"❌ Falha ao enviar email para: {email_usuario}")
            # Mesmo com falha no email, retornamos mensagem genérica por segurança
            return redirect(f'/esqueci-minha-senha?success={mensagem_sucesso}')

        # 6. Redireciona com a mensagem de sucesso genérica
        return redirect(f'/esqueci-minha-senha?success={mensagem_sucesso}')

    except Exception as e:
        print(f"❌ Erro ao gerar link de redefinição: {e}")
        connection.rollback()
        return redirect('/esqueci-minha-senha?error=Houve um erro interno. Tente novamente.')
    finally:
        close_db_connection(connection)

# ----------------------------------------------------
# Rota 3: Página e Lógica de Redefinição de Senha
# ----------------------------------------------------
@auth.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    connection = conectar()
    if not connection:
        return redirect('/login?error=Erro de conexão com o banco. Tente novamente.')

    try:
        cursor = connection.cursor(dictionary=True)
        
        # 1. Validar Token no DB
        cursor.execute(
            'SELECT user_id, expires_at FROM recuperacao_senha WHERE token = %s',
            (token,)
        )
        reset_entry = cursor.fetchone()

        if not reset_entry or reset_entry['expires_at'] < datetime.now():
            print(f"❌ DEBUG - Token inválido ou expirado: {token}")
            # Redireciona para o formulário de login com mensagem de erro
            return redirect('/login?error=O link de redefinição é inválido ou expirou. Por favor, solicite um novo link.')

        user_id = reset_entry['user_id']
        
        # 2. Processar a Nova Senha (se for um POST)
        if request.method == 'POST':
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')

            if nova_senha != confirmar_senha:
                # Exibe o erro na própria página de redefinição
                return render_template('redefinir_senha.html', token=token, error='As senhas não coincidem.')
            
            if len(nova_senha) < 6:
                 # Exibe o erro na própria página de redefinição
                 return render_template('redefinir_senha.html', token=token, error='A senha deve ter pelo menos 6 caracteres.')

            # Criptografar e Salvar Nova Senha
            nova_senha_hash = hash_password(nova_senha)
            cursor.execute(
                'UPDATE usuario SET senha = %s WHERE id_usuario = %s',
                (nova_senha_hash, user_id)
            )
            
            # Desativar/Excluir o Token (Uso único)
            cursor.execute('DELETE FROM recuperacao_senha WHERE token = %s', (token,))
            
            connection.commit()
            print(f"✅ DEBUG - Senha redefinida com sucesso para o user_id: {user_id}")
            
            # Redirecionar para o login com mensagem de sucesso
            return redirect('/login?success=Sua senha foi redefinida com sucesso. Faça login.')

        # 3. Exibir Formulário (se for um GET com token válido)
        return render_template('redefinir_senha.html', token=token)

    except Exception as e:
        print(f"❌ Erro na redefinição de senha: {e}")
        connection.rollback()
        return redirect('/login?error=Houve um erro interno durante a redefinição.')
    finally:
        close_db_connection(connection)