# Demanda Controller.Py
from models.demanda_model import (
    create_demanda,
    get_all_demandas,
    get_demanda_by_id,
    update_demanda,
    delete_demanda,
)
from utils.session import Session
from utils.logger import log_action


def adicionar_demanda(
    data_entrada, solicitante, data_protocolo, oficio, nup_sei, status
):
    """
    Adiciona uma nova demanda

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
    try:
        demanda_id = create_demanda(
            data_entrada, solicitante, data_protocolo, oficio, nup_sei, status
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Cadastro de Demanda: {oficio} (ID: {demanda_id})")

        return demanda_id

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao adicionar demanda: {str(e)}")


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
    codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status
):
    """
    Edita uma demanda

    Args:
        codigo (int): Código da demanda
        data_entrada (str): Data de entrada da demanda
        solicitante (str): Nome do solicitante
        data_protocolo (str): Data de protocolo
        oficio (str): Número do ofício
        nup_sei (str): Número do NUP/SEI
        status (str): Status da demanda
    """
    try:
        update_demanda(
            codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Edição de Demanda: {oficio} (ID: {codigo})")

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao editar demanda: {str(e)}")


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
