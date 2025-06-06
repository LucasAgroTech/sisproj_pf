# Pessoa Fisica Model.Py
from .db_manager import get_connection


def create_pessoa_fisica(nome_completo, cpf=None, email=None, telefone=None):
    """
    Cria um novo registro de pessoa física

    Args:
        nome_completo (str): Nome completo da pessoa
        cpf (str, optional): CPF da pessoa
        email (str, optional): Email da pessoa
        telefone (str, optional): Telefone da pessoa

    Returns:
        int: ID da pessoa física criada
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se já existe um registro com o mesmo CPF
    if cpf:
        cursor.execute("SELECT id FROM pessoa_fisica WHERE cpf=?", (cpf,))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Já existe uma pessoa cadastrada com o CPF {cpf}")

    cursor.execute(
        """
        INSERT INTO pessoa_fisica (nome_completo, cpf, email, telefone)
        VALUES (?, ?, ?, ?)
    """,
        (nome_completo, cpf, email, telefone),
    )

    # Obter o ID da pessoa inserida
    pessoa_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return pessoa_id


def get_all_pessoas_fisicas():
    """
    Retorna todas as pessoas físicas cadastradas

    Returns:
        list: Lista de tuplas com as pessoas físicas
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pessoa_fisica ORDER BY nome_completo")
    pessoas = cursor.fetchall()
    conn.close()

    return [tuple(pessoa) for pessoa in pessoas]


def get_pessoa_fisica_by_id(id_pessoa):
    """
    Obtém uma pessoa física pelo seu ID

    Args:
        id_pessoa (int): ID da pessoa física

    Returns:
        tuple: Dados da pessoa física ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pessoa_fisica WHERE id=?", (id_pessoa,))
    pessoa = cursor.fetchone()
    conn.close()

    if pessoa:
        return tuple(pessoa)
    return None


def get_pessoa_fisica_by_cpf(cpf):
    """
    Obtém uma pessoa física pelo seu CPF

    Args:
        cpf (str): CPF da pessoa física

    Returns:
        tuple: Dados da pessoa física ou None se não encontrada
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pessoa_fisica WHERE cpf=?", (cpf,))
    pessoa = cursor.fetchone()
    conn.close()

    if pessoa:
        return tuple(pessoa)
    return None


def search_pessoas_fisicas(termo_busca):
    """
    Busca pessoas físicas por nome ou CPF

    Args:
        termo_busca (str): Termo a ser buscado no nome ou CPF

    Returns:
        list: Lista de tuplas com as pessoas físicas encontradas
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Adiciona % para busca parcial (LIKE)
    termo = f"%{termo_busca}%"

    cursor.execute(
        """
        SELECT * FROM pessoa_fisica 
        WHERE nome_completo LIKE ? OR cpf LIKE ?
        ORDER BY nome_completo
    """,
        (termo, termo),
    )

    pessoas = cursor.fetchall()
    conn.close()

    return [tuple(pessoa) for pessoa in pessoas]


def update_pessoa_fisica(id_pessoa, nome_completo, cpf=None, email=None, telefone=None):
    """
    Atualiza uma pessoa física

    Args:
        id_pessoa (int): ID da pessoa física
        nome_completo (str): Nome completo da pessoa
        cpf (str, optional): CPF da pessoa
        email (str, optional): Email da pessoa
        telefone (str, optional): Telefone da pessoa
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se já existe outro registro com o mesmo CPF
    if cpf:
        cursor.execute(
            "SELECT id FROM pessoa_fisica WHERE cpf=? AND id<>?", (cpf, id_pessoa)
        )
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Já existe outra pessoa cadastrada com o CPF {cpf}")

    cursor.execute(
        """
        UPDATE pessoa_fisica SET 
            nome_completo=?, cpf=?, email=?, telefone=?
        WHERE id=?
    """,
        (nome_completo, cpf, email, telefone, id_pessoa),
    )

    conn.commit()
    conn.close()


def delete_pessoa_fisica(id_pessoa):
    """
    Exclui uma pessoa física

    Args:
        id_pessoa (int): ID da pessoa física

    Raises:
        ValueError: Se a pessoa tiver contratos vinculados
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se a pessoa tem contratos vinculados
    cursor.execute(
        "SELECT COUNT(*) FROM contrato_pf WHERE id_pessoa_fisica=?", (id_pessoa,)
    )
    count = cursor.fetchone()[0]

    if count > 0:
        conn.close()
        raise ValueError(
            f"Não é possível excluir esta pessoa porque ela possui {count} contrato(s) vinculado(s)"
        )

    cursor.execute("DELETE FROM pessoa_fisica WHERE id=?", (id_pessoa,))
    conn.commit()
    conn.close()
