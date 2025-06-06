# Produto Pf Model.Py
from .db_manager import get_connection


def create_produto_pf(
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
    Cria um novo produto para contrato PF

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
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se o contrato existe e se é de modalidade compatível
    cursor.execute("SELECT modalidade FROM contrato_pf WHERE id=?", (id_contrato,))
    contrato = cursor.fetchone()

    if not contrato:
        conn.close()
        raise ValueError(f"Contrato com ID {id_contrato} não encontrado")

    modalidade = contrato[0]
    if modalidade not in ("BOLSA", "PRODUTO", "RPA"):
        conn.close()
        raise ValueError(
            f"Produtos só podem ser cadastrados para contratos de modalidade Bolsa, Produto ou RPA"
        )

    cursor.execute(
        """
        INSERT INTO produto_pf (
            id_contrato, numero, data_programada, instrumento, 
            data_entrega, status, titulo, valor
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            id_contrato,
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor,
        ),
    )

    # Obter o ID do produto inserido
    produto_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return produto_id


def get_all_produtos_pf():
    """
    Retorna todos os produtos

    Returns:
        list: Lista de tuplas com os produtos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, c.numero_contrato, pf.nome_completo
        FROM produto_pf p
        JOIN contrato_pf c ON p.id_contrato = c.id
        JOIN pessoa_fisica pf ON c.id_pessoa_fisica = pf.id
        ORDER BY p.id DESC
    """
    )
    produtos = cursor.fetchall()
    conn.close()

    return [tuple(produto) for produto in produtos]


def get_produtos_by_contrato(id_contrato):
    """
    Retorna os produtos de um contrato específico

    Args:
        id_contrato (int): ID do contrato

    Returns:
        list: Lista de tuplas com os produtos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, c.numero_contrato, pf.nome_completo
        FROM produto_pf p
        JOIN contrato_pf c ON p.id_contrato = c.id
        JOIN pessoa_fisica pf ON c.id_pessoa_fisica = pf.id
        WHERE p.id_contrato = ?
        ORDER BY p.numero
    """,
        (id_contrato,),
    )
    produtos = cursor.fetchall()
    conn.close()

    return [tuple(produto) for produto in produtos]


def get_produto_by_id(id_produto):
    """
    Obtém um produto pelo seu ID

    Args:
        id_produto (int): ID do produto

    Returns:
        tuple: Dados do produto ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.*, c.numero_contrato, pf.nome_completo
        FROM produto_pf p
        JOIN contrato_pf c ON p.id_contrato = c.id
        JOIN pessoa_fisica pf ON c.id_pessoa_fisica = pf.id
        WHERE p.id = ?
    """,
        (id_produto,),
    )
    produto = cursor.fetchone()
    conn.close()

    if produto:
        return tuple(produto)
    return None


def update_produto_pf(
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
    Atualiza um produto

    Args:
        id_produto (int): ID do produto
        [outros parâmetros iguais ao create_produto_pf]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE produto_pf SET
            numero=?, data_programada=?, instrumento=?, 
            data_entrega=?, status=?, titulo=?, valor=?
        WHERE id=?
    """,
        (
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor,
            id_produto,
        ),
    )

    conn.commit()
    conn.close()


def delete_produto_pf(id_produto):
    """
    Exclui um produto

    Args:
        id_produto (int): ID do produto
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM produto_pf WHERE id=?", (id_produto,))

    conn.commit()
    conn.close()
