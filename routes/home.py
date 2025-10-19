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
    nome = session['nome_usuario']
    return render_template('inicio.html', nome_usuario=nome)

@home.route('/tarefas')
def minhasTarefas():
    return render_template('minhas-tarefas.html')

@home.route('/perfil')
def meuPerfil():
    return render_template('perfil.html')