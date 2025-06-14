# Demanda Controller.Py
from models.demanda_model import (
    create_demanda,
    get_all_demandas,
    get_demanda_by_id,
    update_demanda,
    delete_demanda,
)
from models.db_manager_access import get_connection
from utils.session import Session
from utils.logger import log_action


def adicionar_demanda(
    data_entrada,
    solicitante,
    data_protocolo,
    oficio,
    nup_sei,
):
    """
    Adiciona uma nova demanda

    Args:
        data_entrada (str): Data de entrada
        solicitante (str): Solicitante
        data_protocolo (str): Data do protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI

    Returns:
        int: ID da demanda adicionada
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Inserir demanda
        cursor.execute(
            """
            INSERT INTO demanda (
                data_entrada, solicitante, data_protocolo,
                oficio, nup_sei
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (data_entrada, solicitante, data_protocolo, oficio, nup_sei),
        )

        # Obter o ID da demanda inserida
        cursor.execute("SELECT @@IDENTITY")
        id_demanda = cursor.fetchone()[0]

        conn.commit()
        return id_demanda

    except Exception as e:
        conn.rollback()
        raise Exception(f"Erro ao adicionar demanda: {str(e)}")
    finally:
        conn.close()


def listar_demandas():
    """
    Lista todas as demandas

    Returns:
        list: Lista de demandas
    """
    return get_all_demandas()


def buscar_demanda_por_id(codigo):
    """
    Busca uma demanda pelo seu código

    Args:
        codigo (int): Código da demanda

    Returns:
        tuple: Dados da demanda ou None
    """
    return get_demanda_by_id(codigo)


def editar_demanda(
    codigo_demanda,
    data_entrada,
    solicitante,
    data_protocolo,
    oficio,
    nup_sei,
):
    """
    Edita uma demanda existente

    Args:
        codigo_demanda (int): Código da demanda
        data_entrada (str): Data de entrada
        solicitante (str): Solicitante
        data_protocolo (str): Data do protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI

    Returns:
        bool: True se a edição foi bem sucedida
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Atualizar demanda
        cursor.execute(
            """
            UPDATE demanda SET
                data_entrada = ?, solicitante = ?, data_protocolo = ?,
                oficio = ?, nup_sei = ?
            WHERE codigo = ?
            """,
            (data_entrada, solicitante, data_protocolo, oficio, nup_sei, codigo_demanda),
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise Exception(f"Erro ao editar demanda: {str(e)}")
    finally:
        conn.close()


def excluir_demanda(codigo):
    """
    Exclui uma demanda

    Args:
        codigo (int): Código da demanda
    """
    try:
        # Buscar a demanda antes de excluir (para o log)
        demanda = get_demanda_by_id(codigo)
        oficio = demanda[4] if demanda and len(demanda) > 4 else f"ID: {codigo}"

        delete_demanda(codigo)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Exclusão de Demanda: {oficio} (ID: {codigo})")

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao excluir demanda: {str(e)}")
