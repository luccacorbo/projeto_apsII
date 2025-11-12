import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

def conectar():
    try:
        # --- INÍCIO DA MUDANÇA ---
        
        # 1. Pega as variáveis do Railway PRIMEIRO.
        # 2. Se não achar, usa as do seu .env (DB_HOST, DB_USER...)
        db_host = os.getenv("MYSQLHOST", os.getenv("DB_HOST"))
        db_user = os.getenv("MYSQLUSER", os.getenv("DB_USER"))
        db_pass = os.getenv("MYSQLPASSWORD", os.getenv("DB_PASSWORD"))
        db_name = os.getenv("MYSQLDATABASE", os.getenv("DB_NAME"))
        
        # 3. Pega a PORTA (O MAIS IMPORTANTE)
        # O Railway usa uma porta aleatória. Localmente, usamos 3306.
        # Convertemos para int, pois a variável de ambiente é string.
        db_port = int(os.getenv("MYSQLPORT", 3306))
        
        # Debug:
        print(f"🔍 DEBUG CONEXÃO - Conectando em: {db_host}:{db_port} com DB: {db_name}")

        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            port=db_port  # <-- ADICIONAMOS A PORTA AQUI
        )
        
        # --- FIM DA MUDANÇA ---
        
        print("✅ DEBUG CONEXÃO - Sucesso!")
        return conn
        
    except Error as e:
        print(f"❌ ERRO AO CONECTAR AO MYSQL: {e}")
        return None

def close_db_connection(connection):
    """
    Fecha conexão com o banco
    """
    if connection:
        connection.close()

def hash_password(senha):
    """Gera hash para uma senha"""
    return generate_password_hash(senha)

def check_password(senha_hash, senha):
    """Verifica se a senha corresponde ao hash"""
    return check_password_hash(senha_hash, senha)