from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar  # Supondo que você tenha este arquivo para a conexão
import mysql.connector

home = Blueprint('home', __name__)

# Rota para a página inicial (landing page), pode ser diferente da home do usuário logado.
@home.route('/inicio')
def rt_Projeto():
    if 'logged_in' in session:
        # Se o usuário estiver logado, talvez seja melhor redirecioná-lo para /home
        return redirect(url_for('home.retornaInicio'))
    return render_template('inicio.html')

# Rota para o painel principal do usuário após o login
@home.route('/home')
def retornaInicio():
    # 1. VERIFICAÇÃO DE LOGIN
    if 'user_id' not in session:
        return redirect('/login')
    
    # 2. BUSCA DE PROJETOS NO BANCO DE DADOS
    connection = conectar()
    projetos = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            # Busca os projetos que o usuário criou
            cursor.execute("""
                SELECT * FROM projetos 
                WHERE id_criador = %s 
                ORDER BY data_criacao DESC
            """, (session['user_id'],))
            projetos = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Erro ao buscar projetos: {e}")
        finally:
            connection.close()
    
    # 3. EXTRAÇÃO DO PRIMEIRO NOME
    # Pega o nome completo da sessão (ex: "Allan Vieira Siqueira")
    nome_completo = session.get('user_name', 'Usuário') 
    
    # Divide o nome pelo espaço e pega a primeira parte (ex: "Allan")
    primeiro_nome = nome_completo.split(' ')[0]

    # 4. RENDERIZA O TEMPLATE, ENVIANDO AS VARIÁVEIS CORRETAS
    return render_template('inicio.html', 
                           primeiro_nome=primeiro_nome, 
                           id_projetos=projetos)

@home.route('/tarefas')
def minhasTarefas():
    # Aqui também seria bom adicionar a verificação de login
    if 'user_id' not in session:
        return redirect('/login')
    
    # --- MUDANÇA ADICIONADA AQUI ---
    nome_completo = session.get('user_name', 'Visitante')
    primeiro_nome = nome_completo.split(' ')[0]
    # --- FIM DA MUDANÇA ---

    return render_template('minhas-tarefas.html', primeiro_nome=primeiro_nome)

@home.route('/perfil')
def meuPerfil():
    # E aqui também
    if 'user_id' not in session:
        return redirect('/login')

    # --- MUDANÇA ADICIONADA AQUI ---
    nome_completo = session.get('user_name', 'Visitante')
    primeiro_nome = nome_completo.split(' ')[0]
    # --- FIM DA MUDANÇA ---

    return render_template('perfil.html', primeiro_nome=primeiro_nome)