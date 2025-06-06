# Produto Pf Controller.Py
from models.produto_pf_model import (
    create_produto_pf,
    get_all_produtos_pf,
    get_produtos_by_contrato,
    get_produto_by_id,
    update_produto_pf,
    delete_produto_pf,
)
from utils.session import Session
from utils.logger import log_action


def adicionar_produto(
    id_contrato,
    numero,
    data_programada=None,
    instrumento=None,
    data_entrega=None,
    status="programado",
    titulo=None,
    valor=0,
):
    """
    Adiciona um novo produto para contrato PF

    Args:
        id_contrato (int): ID do contrato
        numero (str): Número ou identificação do produto
        data_programada (str, optional): Data programada
        instrumento (str, optional): Instrumento
        data_entrega (str, optional): Data de entrega
        status (str, optional): Status do produto (programado, em_execucao, entregue, cancelado)
        titulo (str, optional): Título do produto
        valor (float, optional): Valor do produto

    Returns:
        int: ID do produto criado
    """
    try:
        # Converter valor para float
        if valor:
            valor = float(valor)

        id_produto = create_produto_pf(
            id_contrato,
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor,
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1], f"Cadastro de Produto para Contrato PF ID: {id_contrato}"
            )

        return id_produto

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))


def listar_produtos():
    """
    Lista todos os produtos

    Returns:
        list: Lista de produtos
    """
    return get_all_produtos_pf()


def listar_produtos_por_contrato(id_contrato):
    """
    Lista os produtos de um contrato específico

    Args:
        id_contrato (int): ID do contrato

    Returns:
        list: Lista de produtos do contrato
    """
    return get_produtos_by_contrato(id_contrato)


def buscar_produto_por_id(id_produto):
    """
    Busca um produto pelo ID

    Args:
        id_produto (int): ID do produto

    Returns:
        tuple: Dados do produto ou None
    """
    return get_produto_by_id(id_produto)


def editar_produto(
    id_produto,
    numero,
    data_programada=None,
    instrumento=None,
    data_entrega=None,
    status="programado",
    titulo=None,
    valor=0,
):
    """
    Edita um produto

    Args:
        id_produto (int): ID do produto
        [outros parâmetros iguais ao adicionar_produto]
    """
    try:
        # Converter valor para float
        if valor:
            valor = float(valor)

        update_produto_pf(
            id_produto,
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor,
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Edição de Produto ID: {id_produto}")

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao editar produto: {str(e)}")


def excluir_produto(id_produto):
    """
    Exclui um produto

    Args:
        id_produto (int): ID do produto
    """
    try:
        delete_produto_pf(id_produto)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Exclusão de Produto ID: {id_produto}")

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao excluir produto: {str(e)}")
