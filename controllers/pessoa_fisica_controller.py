# Pessoa Fisica Controller.Py
from models.pessoa_fisica_model import (
    create_pessoa_fisica,
    get_all_pessoas_fisicas,
    get_pessoa_fisica_by_id,
    get_pessoa_fisica_by_cpf,
    search_pessoas_fisicas,
    update_pessoa_fisica,
    delete_pessoa_fisica,
)
from utils.session import Session
from utils.logger import log_action


def adicionar_pessoa_fisica(nome_completo, cpf=None, email=None, telefone=None):
    """
    Adiciona uma nova pessoa física

    Args:
        nome_completo (str): Nome completo da pessoa
        cpf (str, optional): CPF da pessoa
        email (str, optional): Email da pessoa
        telefone (str, optional): Telefone da pessoa

    Returns:
        int: ID da pessoa física criada
    """
    try:
        id_pessoa = create_pessoa_fisica(nome_completo, cpf, email, telefone)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Cadastro de Pessoa Física: {nome_completo}")

        return id_pessoa

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))


def listar_pessoas():
    """
    Lista todas as pessoas físicas cadastradas

    Returns:
        list: Lista de pessoas físicas
    """
    return get_all_pessoas_fisicas()


def buscar_pessoa_por_id(id_pessoa):
    """
    Busca uma pessoa física pelo ID

    Args:
        id_pessoa (int): ID da pessoa física

    Returns:
        tuple: Dados da pessoa física ou None
    """
    return get_pessoa_fisica_by_id(id_pessoa)


def buscar_pessoa_por_cpf(cpf):
    """
    Busca uma pessoa física pelo CPF

    Args:
        cpf (str): CPF da pessoa física

    Returns:
        tuple: Dados da pessoa física ou None
    """
    return get_pessoa_fisica_by_cpf(cpf)


def buscar_pessoas(termo_busca):
    """
    Busca pessoas físicas por nome ou CPF

    Args:
        termo_busca (str): Termo para busca

    Returns:
        list: Lista de pessoas físicas encontradas
    """
    return search_pessoas_fisicas(termo_busca)


def editar_pessoa_fisica(id_pessoa, nome_completo, cpf=None, email=None, telefone=None):
    """
    Edita os dados de uma pessoa física

    Args:
        id_pessoa (int): ID da pessoa física
        nome_completo (str): Nome completo da pessoa
        cpf (str, optional): CPF da pessoa
        email (str, optional): Email da pessoa
        telefone (str, optional): Telefone da pessoa
    """
    try:
        update_pessoa_fisica(id_pessoa, nome_completo, cpf, email, telefone)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1],
                f"Edição de Pessoa Física: {nome_completo} (ID: {id_pessoa})",
            )

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))


def excluir_pessoa_fisica(id_pessoa):
    """
    Exclui uma pessoa física

    Args:
        id_pessoa (int): ID da pessoa física
    """
    try:
        # Buscar o nome da pessoa antes de excluir (para o log)
        pessoa = get_pessoa_fisica_by_id(id_pessoa)
        nome = pessoa[1] if pessoa else f"ID: {id_pessoa}"

        delete_pessoa_fisica(id_pessoa)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Exclusão de Pessoa Física: {nome}")

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))
