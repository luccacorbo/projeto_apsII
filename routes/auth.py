# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar
import mysql.connector

auth = Blueprint('auth', __name__)

@auth.route("/")
def home():
    return render_template("login.html")

#retorna para a pagina de login
@auth.route('/login')
def retonarlogin():
    return render_template('login.html')

#login do usuario
@auth.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    senha = request.form["senha"]

    db = conectar()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT email, senha, nome FROM usuarios WHERE email=%s AND senha=%s", (email, senha))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        # 1. ARMAZENAR O NOME DO USUÁRIO NA SESSÃO
        # Assumindo que o campo na tabela é 'nome'
        session["logged_in"] = True # Adiciona um indicador de que está logado
        session["usuario"] = user["email"] 
        
        # CHAVE CORRETA: O NOME COMPLETO do usuário
        session["nome_usuario"] = user["nome"]  # <-- ESTA É A CHAVE!
        
        # Remova session["senha"] - Nunca armazene senhas na sessão por segurança!
        
        return redirect(url_for("work.rt_Espaco")) 
    
#criação de cadastro
@auth.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]
        confirmar = request.form["confirmar"]

        if senha != confirmar:
            flash("As senhas não coincidem!")
            return redirect(url_for("auth.cadastro"))

        try:
            db = conectar()
            cursor = db.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)", (nome, email, senha))
            db.commit()
            cursor.close()
            db.close()

            flash("Conta criada com sucesso! Faça login.")
            return redirect(url_for("auth.home"))
        except mysql.connector.IntegrityError:
            flash("E-mail já cadastrado!")
            return redirect(url_for("auth.cadastro"))

    return render_template("cadastro.html")
