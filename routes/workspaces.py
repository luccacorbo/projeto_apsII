from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar
import mysql.connector

work = Blueprint('work', __name__)

@work.route('/inicio')
def rt_Espaco():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
        
    # 3. PASSA PARA O TEMPLATE
    nome = session['nome_usuario']
    return render_template('inicio.html', nome_usuario=nome) # Envia a variável 'nome_usuario'