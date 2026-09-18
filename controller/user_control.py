from auth import conecta_supabase
import pandas as pd
import bcrypt

def criar_usuario(nome, username, perfil):
    
    nome = nome.title()
    username = username.lower()
    user_reset = username.split('.')[0]
    password = user_reset + "@AltoValor"
    senha = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    INSERT INTO tbusuarios (nome, username, senha, perfil)
    VALUES (%s, %s, %s, %s);
    """
    cursor.execute(query, (nome, username, senha, perfil))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def editar_usuario(id, nome, username, perfil):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    UPDATE tbusuarios SET nome = %s, username = %s, perfil = %s WHERE id = %s;
    """
    cursor.execute(query, (nome, username, perfil, id))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def deletar_usuario(id):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    UPDATE tbusuarios SET is_ativo = False WHERE id = %s;
    """
    cursor.execute(query, (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def listar_usuarios():
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    SELECT id, nome, username, perfil FROM tbusuarios WHERE is_ativo = '1';
    """
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])
    cursor.close()
    conn.close()
    # 1️⃣ Mapa para exibição
    user_map = {
        f"{row['nome']} ({row['username']})": row['id']
        for _, row in df.iterrows()
    }

    # 2️⃣ Dicionário completo por ID
    usuarios_dict = {
        row['id']: row.to_dict()
        for _, row in df.iterrows()
    }

    display_options = list(user_map.keys())

    return user_map, usuarios_dict, display_options

def validar_submissao(nome, username, perfil):

        if len(nome.strip()) <= 6:
            return "Nome deve ter mais de 6 caracteres"
        
        elif len(username.strip()) <= 6:
            return "Username deve ter mais de 6 caracteres"
    
        else:
            if validar_repeticao(nome, username) == False:
                return "Usuário já existe"
            else:
                return "Continue"

def validar_repeticao(nome, username):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    SELECT * FROM tbusuarios WHERE nome = %s OR username = %s;
    """
    cursor.execute(query, (nome, username))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if result:
        return False
    else:
        return True

def resetar_senha(id, username):
    user_reset = username.split('.')[0]
    password = user_reset + "@AltoValor"
    senha = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    UPDATE tbusuarios SET senha = %s WHERE id = %s;
    """
    cursor.execute(query, (senha, id))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def alterar_senha(username, senha):
    senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    UPDATE tbusuarios SET senha = %s WHERE username = %s;
    """
    cursor.execute(query, (senha, username))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def get_perfil():
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    SELECT perfil FROM tbperfil;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

    lista = []
    for i in df.iterrows():
        lista.append(i[1]['perfil'])
        
    cursor.close()
    conn.close()
    return lista