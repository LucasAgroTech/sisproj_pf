# User Model.Py
from .db_manager import get_connection


def authenticate(username, password):
    """
    Autentica um usuário com base no nome de usuário e senha

    Args:
        username (str): Nome de usuário
        password (str): Senha

    Returns:
        tuple: Dados do usuário ou None se a autenticação falhar
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, password)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        return tuple(user)
    return None
