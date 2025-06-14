# Logger.Py
from models.db_manager_access import get_connection


def log_action(usuario, acao):
    """
    Registra uma ação do usuário no log do sistema

    Args:
        usuario (str): Nome do usuário
        acao (str): Descrição da ação realizada
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (usuario, acao) VALUES (?, ?)", (usuario, acao))
    conn.commit()
    conn.close()
