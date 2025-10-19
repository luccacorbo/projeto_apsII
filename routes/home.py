from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar
import mysql.connector

home = Blueprint('home', __name__)

@home.route('/inicio')
def rt_Projeto():
    if 'logged_in' not in session:
        return render_template('inicio.html')
        
    # 3. PASSA PARA O TEMPLATE
    nome = session['nome_usuario']
    return render_template('inicio.html', nome_usuario=nome) # Envia a variável 'nome_usuario'

# retonar para a pagina inicial 
@home.route('/home')
def retornaInicio():
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        return redirect('/login')
    
    # Buscar o nome da sessão (agora deve existir)
    nome_usuario = session.get('user_name', 'Usuário')
    # ou use: nome_usuario = session.get('nome_usuario', 'Usuário')
    
    # Renderizar o template passando a variável
    return render_template('inicio.html', nome_usuario=nome_usuario)


@home.route('/tarefas')
def minhasTarefas():
    return render_template('minhas-tarefas.html')

@home.route('/perfil')
def meuPerfil():
    return render_template('perfil.html')