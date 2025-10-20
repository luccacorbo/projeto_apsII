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
    # ⚠️ VERIFICAÇÃO DE LOGIN
    if 'user_id' not in session:
        return redirect('/login')
    
    connection = conectar()
    projetos = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
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
    
    nome_usuario = session.get('user_name', 'Usuário')
    return render_template('inicio.html', 
                         nome_usuario=nome_usuario, 
                         projetos=projetos)

@home.route('/tarefas')
def minhasTarefas():
    return render_template('minhas-tarefas.html')

@home.route('/perfil')
def meuPerfil():
    return render_template('perfil.html')