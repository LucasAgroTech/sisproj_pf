# Demanda Model.Py
from .db_manager import get_connection


def create_demanda(data_entrada, solicitante, data_protocolo, oficio, nup_sei, status):
    """
    Cria uma nova demanda

    Args:
        data_entrada (str): Data de entrada da demanda
        solicitante (str): Nome do solicitante
        data_protocolo (str): Data de protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI
        status (str): Status da demanda

    Returns:
        int: ID da demanda criada
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO demanda (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status),
    )

    # Obter o ID da demanda inserida
    demanda_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return demanda_id


def get_all_demandas():
    """
    Retorna todas as demandas

    Returns:
        list: Lista de tuplas com as demandas
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM demanda ORDER BY codigo DESC")
    demandas = cursor.fetchall()
    conn.close()

    return [tuple(demanda) for demanda in demandas]


def get_demanda_by_id(codigo):
    """
    Obtém uma demanda pelo seu código

    Args:
        codigo (int): Código da demanda

    Returns:
        tuple: Dados da demanda ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM demanda WHERE codigo=?", (codigo,))
    demanda = cursor.fetchone()
    conn.close()

    if demanda:
        return tuple(demanda)
    return None


def update_demanda(
    codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status
):
    """
    Atualiza uma demanda

    Args:
        codigo (int): Código da demanda
        data_entrada (str): Data de entrada da demanda
        solicitante (str): Nome do solicitante
        data_protocolo (str): Data de protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI
        status (str): Status da demanda
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE demanda SET 
            data_entrada=?, solicitante=?, data_protocolo=?, oficio=?, nup_sei=?, status=?
        WHERE codigo=?
    """,
        (data_entrada, solicitante, data_protocolo, oficio, nup_sei, status, codigo),
    )
    conn.commit()
    conn.close()


def delete_demanda(codigo):
    """
    Exclui uma demanda

    Args:
        codigo (int): Código da demanda
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM demanda WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
