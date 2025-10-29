from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import conectar
import mysql.connector

home = Blueprint('home', __name__)

@home.route('/inicio')
def rt_Projeto():
    if 'logged_in' in session:
        return redirect(url_for('home.retornaInicio'))
    return render_template('inicio.html')

# Rota para o painel principal do usuário após o login
@home.route('/home')
def retornaInicio():
    # 1. VERIFICAÇÃO DE LOGIN
    if 'user_id' not in session:
        return redirect('/login')
    
    # 2. BUSCA DE PROJETOS NO BANCO DE DADOS - CORREÇÃO AQUI
    connection = conectar()
    projetos = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # ✅ CORREÇÃO: Buscar projetos onde usuário é CRIADOR OU MEMBRO
            cursor.execute("""
                SELECT DISTINCT 
                    p.id_projeto,
                    p.nome,
                    p.descricao,
                    p.data_criacao,
                    u.nome as criador_nome,
                    u.id_usuario as id_criador,
                    -- Identificar se o usuário atual é o criador
                    CASE 
                        WHEN p.id_criador = %s THEN 1 
                        ELSE 0 
                    END as eh_criador
                FROM projetos p
                JOIN usuario u ON p.id_criador = u.id_usuario
                LEFT JOIN projeto_membros pm ON p.id_projeto = pm.id_projeto
                WHERE p.id_criador = %s OR pm.id_usuario = %s
                ORDER BY p.data_criacao DESC
            """, (session['user_id'], session['user_id'], session['user_id']))
            
            projetos = cursor.fetchall()
            cursor.close()
            
            print(f"✅ Projetos encontrados: {len(projetos)}")  # Debug
            
        except Exception as e:
            print(f"❌ Erro ao buscar projetos: {e}")
        finally:
            connection.close()
    
    # 3. EXTRAÇÃO DO PRIMEIRO NOME
    nome_completo = session.get('user_name', 'Usuário') 
    primeiro_nome = nome_completo.split(' ')[0]

    # 4. RENDERIZA O TEMPLATE - CORREÇÃO AQUI
    # ✅ CORREÇÃO: Enviar 'projetos' em vez de 'id_projetos'
    return render_template('inicio.html', 
                           primeiro_nome=primeiro_nome, 
                           projetos=projetos)  # ← NOME CORRETO DA VARIÁVEL

@home.route('/tarefas')
def minhasTarefas():
    if 'user_id' not in session:
        return redirect('/login')
    
    nome_completo = session.get('user_name', 'Visitante')
    primeiro_nome = nome_completo.split(' ')[0]

    return render_template('minhas-tarefas.html', primeiro_nome=primeiro_nome)

@home.route('/perfil')
def meuPerfil():
    if 'user_id' not in session:
        return redirect('/login')

    nome_completo = session.get('user_name', 'Visitante')
    primeiro_nome = nome_completo.split(' ')[0]

    return render_template('perfil.html', primeiro_nome=primeiro_nome)