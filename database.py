import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

def conectar():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
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