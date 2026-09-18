from auth import conecta_supabase
import bcrypt

def login(login):
    conn = conecta_supabase()
    cursor = conn.cursor()
    query = """
    SELECT u.senha, u.perfil FROM tbusuarios u
    WHERE u.username = %s;
    """
    cursor.execute(query, (login, ))
    result = cursor.fetchone()
    # Verifica se o usuário existe
    if result:
        senha_bd, perfil_bd = result  # Extrai a senha e perfil do resultado
        return senha_bd, perfil_bd
    else:
        return None, None

def autenticar_usuario(username, password):
    senha, perfil = login(username)

    if senha is None:
        return None

    if isinstance(senha, str):
        senha = senha.encode('utf-8')

    password = password.encode('utf-8')

    if bcrypt.checkpw(password, senha):
        return perfil
    else:
        return None