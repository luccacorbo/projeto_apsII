# migrate_passwords.py
from database import hash_password, conectar

def migrate_passwords():
    connection = conectar()
    
    if connection is None:
        print("❌ Erro ao conectar ao banco de dados")
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # PRIMEIRO: Alterar a coluna senha para VARCHAR(255)
        print("🔧 Alterando coluna senha para VARCHAR(255)...")
        cursor.execute("ALTER TABLE usuario MODIFY COLUMN senha VARCHAR(255)")
        connection.commit()
        print("✅ Coluna senha alterada com sucesso!")
        
        # DEPOIS: Migrar as senhas
        cursor.execute("SELECT id_usuario, senha FROM usuario")
        usuarios = cursor.fetchall()
        
        print(f"🔍 Encontrados {len(usuarios)} usuários para migrar")
        
        for usuario in usuarios:
            # Se a senha não estiver hasheada (não começa com $2b$)
            if not usuario['senha'].startswith('$2b$'):
                senha_hash = hash_password(usuario['senha'])
                cursor.execute(
                    "UPDATE usuario SET senha = %s WHERE id_usuario = %s",
                    (senha_hash, usuario['id_usuario'])
                )
                print(f"✅ Senha do usuário {usuario['id_usuario']} atualizada")
            else:
                print(f"⏭️  Usuário {usuario['id_usuario']} já tem senha hasheada")
        
        connection.commit()
        print("🎉 Migração de senhas concluída!")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    migrate_passwords()