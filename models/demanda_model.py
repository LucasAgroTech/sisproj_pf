# Demanda Model.Py
from .db_manager_access import get_connection, validate_list_value


def create_demanda(data_entrada, solicitante, data_protocolo, oficio, nup_sei):
    """
    Cria uma nova demanda

    Args:
        data_entrada (str): Data de entrada da demanda
        solicitante (str): Nome do solicitante
        data_protocolo (str): Data de protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI

    Returns:
        int: ID da demanda criada
        
    Raises:
        ValueError: Se o solicitante não existir na tabela lists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Validar solicitante
        if not validate_list_value(cursor, "solicitante", solicitante):
            raise ValueError(f"Solicitante '{solicitante}' não encontrado na lista de valores válidos")
            
        cursor.execute(
            """
            INSERT INTO demanda (data_entrada, solicitante, data_protocolo, oficio, nup_sei)
            VALUES (?, ?, ?, ?, ?)
        """,
            (data_entrada, solicitante, data_protocolo, oficio, nup_sei),
        )

        # Obter o ID da demanda inserida usando SELECT @@IDENTITY
        cursor.execute("SELECT @@IDENTITY")
        demanda_id = cursor.fetchone()[0]
        
        conn.commit()
        return demanda_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


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


def update_demanda(codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei):
    """
    Atualiza uma demanda existente

    Args:
        codigo (int): Código da demanda
        data_entrada (str): Data de entrada da demanda
        solicitante (str): Nome do solicitante
        data_protocolo (str): Data de protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI
        
    Raises:
        ValueError: Se o solicitante não existir na tabela lists
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Validar solicitante
        if not validate_list_value(cursor, "solicitante", solicitante):
            raise ValueError(f"Solicitante '{solicitante}' não encontrado na lista de valores válidos")
            
        cursor.execute(
            """
            UPDATE demanda SET 
                data_entrada=?, solicitante=?, data_protocolo=?, oficio=?, nup_sei=?
            WHERE codigo=?
        """,
            (data_entrada, solicitante, data_protocolo, oficio, nup_sei, codigo),
        )
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
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
