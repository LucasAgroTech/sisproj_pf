# Contrato Pf Model.Py
from .db_manager_access import get_connection, validate_list_value
from datetime import datetime


def create_contrato_pf(
    codigo_demanda,
    id_pessoa_fisica,
    instituicao,
    instrumento,
    subprojeto,
    ta,
    pta,
    acao,
    resultado,
    meta,
    modalidade,
    natureza_demanda,
    numero_contrato,
    vigencia_inicial,
    vigencia_final,
    meses,
    status_contrato,
    remuneracao,
    intersticio,
    valor_intersticio=0,
    valor_complementar=0,
    total_contrato=0,
    observacoes=None,
    lotacao=None,
    exercicio=None
):
    """
    Cria um novo contrato de pessoa física

    Args:
        codigo_demanda (int): Código da demanda
        id_pessoa_fisica (int): ID da pessoa física
        instituicao (str): Instituição
        instrumento (str): Instrumento
        subprojeto (str): Subprojeto
        ta (str): TA
        pta (str): PTA
        acao (str): Ação
        resultado (str): Resultado
        meta (str): Meta
        modalidade (str): Modalidade do contrato (bolsa, produto, RPA, CLT)
        natureza_demanda (str): Natureza da demanda (novo, renovacao)
        numero_contrato (str): Número do contrato
        vigencia_inicial (str): Data de início da vigência
        vigencia_final (str): Data final da vigência
        meses (int): Quantidade de meses
        status_contrato (str): Status do contrato
        remuneracao (float): Valor da remuneração
        intersticio (int): Se tem interstício (0=não, 1=sim)
        valor_intersticio (float, optional): Valor do interstício
        valor_complementar (float, optional): Valor complementar
        total_contrato (float, optional): Valor total do contrato
        observacoes (str, optional): Observações
        lotacao (str, optional): Lotação do contrato
        exercicio (str, optional): Exercício do contrato

    Returns:
        int: ID do contrato criado
        
    Raises:
        ValueError: Se modalidade, natureza_demanda, status_contrato, lotacao ou exercicio não existirem na tabela lists
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Validar valores contra a tabela lists
        validations = [
            ("modalidade_contrato", modalidade),
            ("natureza_demanda", natureza_demanda),
            ("status_contrato", status_contrato),
            ("lotacao", lotacao),
            ("exercicio", exercicio)
        ]
        
        for column, value in validations:
            if not validate_list_value(cursor, column, value):
                raise ValueError(f"Valor '{value}' não encontrado na lista de {column}")

        # Calcula o total se não for fornecido
        if total_contrato == 0:
            total_contrato = (remuneracao * meses) + valor_intersticio + valor_complementar

        cursor.execute(
            """
            INSERT INTO contrato_pf (
                codigo_demanda, id_pessoa_fisica, instituicao, instrumento, subprojeto, ta, pta, acao,
                resultado, meta, modalidade, natureza_demanda, numero_contrato, vigencia_inicial, 
                vigencia_final, meses, status_contrato, remuneracao, intersticio, valor_intersticio, 
                valor_complementar, total_contrato, observacoes, lotacao, exercicio
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                codigo_demanda,
                id_pessoa_fisica,
                instituicao,
                instrumento,
                subprojeto,
                ta,
                pta,
                acao,
                resultado,
                meta,
                modalidade,
                natureza_demanda,
                numero_contrato,
                vigencia_inicial,
                vigencia_final,
                meses,
                status_contrato,
                remuneracao,
                intersticio,
                valor_intersticio,
                valor_complementar,
                total_contrato,
                observacoes,
                lotacao,
                exercicio
            ),
        )

        # Obter o ID do contrato inserido usando SELECT @@IDENTITY
        cursor.execute("SELECT @@IDENTITY")
        contrato_id = cursor.fetchone()[0]

        conn.commit()
        return contrato_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_contratos_pf():
    """
    Retorna todos os contratos de pessoa física

    Returns:
        list: Lista de tuplas com os contratos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, p.nome_completo 
        FROM [contrato_pf] AS c 
        INNER JOIN [pessoa_fisica] AS p ON c.id_pessoa_fisica = p.id
        ORDER BY c.id DESC
        """
    )
    contratos = cursor.fetchall()
    conn.close()

    return [tuple(contrato) for contrato in contratos]


def get_contratos_by_pessoa(id_pessoa_fisica):
    """
    Retorna os contratos de uma pessoa física específica

    Args:
        id_pessoa_fisica (int): ID da pessoa física

    Returns:
        list: Lista de tuplas com os contratos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, p.nome_completo 
        FROM ([contrato_pf] AS c
        INNER JOIN [pessoa_fisica] AS p ON c.id_pessoa_fisica = p.id)
        WHERE c.id_pessoa_fisica = ?
        ORDER BY c.id DESC
        """,
        (id_pessoa_fisica,),
    )
    contratos = cursor.fetchall()
    conn.close()

    return [tuple(contrato) for contrato in contratos]


def get_contratos_by_demanda(codigo_demanda):
    """
    Retorna os contratos vinculados a uma demanda específica

    Args:
        codigo_demanda (int): Código da demanda

    Returns:
        list: Lista de tuplas com os contratos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, p.nome_completo 
        FROM ([contrato_pf] AS c
        INNER JOIN [pessoa_fisica] AS p ON c.id_pessoa_fisica = p.id)
        WHERE c.codigo_demanda = ?
        ORDER BY c.id DESC
        """,
        (codigo_demanda,),
    )
    contratos = cursor.fetchall()
    conn.close()

    return [tuple(contrato) for contrato in contratos]


def get_contrato_by_id(id_contrato):
    """
    Obtém um contrato pelo seu ID

    Args:
        id_contrato (int): ID do contrato

    Returns:
        tuple: Dados do contrato ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT c.*, p.nome_completo 
        FROM ([contrato_pf] AS c
        INNER JOIN [pessoa_fisica] AS p ON c.id_pessoa_fisica = p.id)
        WHERE c.id = ?
        """,
        (id_contrato,),
    )
    contrato = cursor.fetchone()
    conn.close()

    if contrato:
        return tuple(contrato)
    return None


def update_contrato_pf(
    id_contrato,
    codigo_demanda,
    id_pessoa_fisica,
    instituicao,
    instrumento,
    subprojeto,
    ta,
    pta,
    acao,
    resultado,
    meta,
    modalidade,
    natureza_demanda,
    numero_contrato,
    vigencia_inicial,
    vigencia_final,
    meses,
    status_contrato,
    remuneracao,
    intersticio,
    valor_intersticio=0,
    valor_complementar=0,
    total_contrato=0,
    observacoes=None,
    lotacao=None,
    exercicio=None
):
    """
    Atualiza um contrato de pessoa física

    Args:
        id_contrato (int): ID do contrato
        [outros parâmetros iguais ao create_contrato_pf]
        
    Raises:
        ValueError: Se modalidade, natureza_demanda, status_contrato, lotacao ou exercicio não existirem na tabela lists
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Validar valores contra a tabela lists
        validations = [
            ("modalidade_contrato", modalidade),
            ("natureza_demanda", natureza_demanda),
            ("status_contrato", status_contrato),
            ("lotacao", lotacao),
            ("exercicio", exercicio)
        ]
        
        for column, value in validations:
            if not validate_list_value(cursor, column, value):
                raise ValueError(f"Valor '{value}' não encontrado na lista de {column}")

        # Calcula o total se não for fornecido
        if total_contrato == 0:
            total_contrato = (remuneracao * meses) + valor_intersticio + valor_complementar

        cursor.execute(
            """
            UPDATE contrato_pf SET
                codigo_demanda=?, id_pessoa_fisica=?, instituicao=?, instrumento=?, subprojeto=?, ta=?, pta=?, acao=?,
                resultado=?, meta=?, modalidade=?, natureza_demanda=?, numero_contrato=?, vigencia_inicial=?, 
                vigencia_final=?, meses=?, status_contrato=?, remuneracao=?, intersticio=?, valor_intersticio=?, 
                valor_complementar=?, total_contrato=?, observacoes=?, lotacao=?, exercicio=?
            WHERE id=?
        """,
            (
                codigo_demanda,
                id_pessoa_fisica,
                instituicao,
                instrumento,
                subprojeto,
                ta,
                pta,
                acao,
                resultado,
                meta,
                modalidade,
                natureza_demanda,
                numero_contrato,
                vigencia_inicial,
                vigencia_final,
                meses,
                status_contrato,
                remuneracao,
                intersticio,
                valor_intersticio,
                valor_complementar,
                total_contrato,
                observacoes,
                lotacao,
                exercicio,
                id_contrato,
            ),
        )

        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def delete_contrato_pf(id_contrato):
    """
    Exclui um contrato de pessoa física

    Args:
        id_contrato (int): ID do contrato

    Raises:
        ValueError: Se o contrato tiver aditivos ou produtos vinculados
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verificar se o contrato tem aditivos vinculados
    cursor.execute(
        "SELECT COUNT(*) FROM aditivo_pf WHERE id_contrato=?", (id_contrato,)
    )
    count_aditivos = cursor.fetchone()[0]

    if count_aditivos > 0:
        conn.close()
        raise ValueError(
            f"Não é possível excluir este contrato porque ele possui {count_aditivos} aditivo(s) vinculado(s)"
        )

    # Verificar se o contrato tem produtos vinculados
    cursor.execute(
        "SELECT COUNT(*) FROM produto_pf WHERE id_contrato=?", (id_contrato,)
    )
    count_produtos = cursor.fetchone()[0]

    if count_produtos > 0:
        conn.close()
        raise ValueError(
            f"Não é possível excluir este contrato porque ele possui {count_produtos} produto(s) vinculado(s)"
        )

    cursor.execute("DELETE FROM contrato_pf WHERE id=?", (id_contrato,))
    conn.commit()
    conn.close()


def search_contratos_pf(termo_busca):
    """
    Busca contratos por número, nome da pessoa ou modalidade

    Args:
        termo_busca (str): Termo a ser buscado

    Returns:
        list: Lista de tuplas com os contratos encontrados
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Adiciona % para busca parcial (LIKE)
    termo = f"%{termo_busca}%"

    cursor.execute(
        """
        SELECT c.*, p.nome_completo 
        FROM contrato_pf c
        JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
        WHERE c.numero_contrato LIKE ? 
        OR p.nome_completo LIKE ? 
        OR c.modalidade LIKE ?
        ORDER BY c.id DESC
    """,
        (termo, termo, termo),
    )

    contratos = cursor.fetchall()
    conn.close()

    return [tuple(contrato) for contrato in contratos]


def update_total_contrato(id_contrato):
    """
    Recalcula e atualiza o valor total do contrato incluindo aditivos

    Args:
        id_contrato (int): ID do contrato
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar dados originais do contrato (valores base antes dos aditivos)
    # Para isso, precisamos recalcular baseado na remuneração e meses originais
    cursor.execute(
        """
        SELECT intersticio, valor_intersticio, valor_complementar
        FROM contrato_pf WHERE id=?
    """,
        (id_contrato,),
    )

    contrato = cursor.fetchone()

    if contrato:
        # Valores fixos do contrato original
        intersticio = int(contrato[0]) if contrato[0] else 0
        valor_intersticio = (
            float(contrato[1]) if contrato[1] and intersticio == 1 else 0
        )
        valor_complementar_original = float(contrato[2]) if contrato[2] else 0

        # Buscar a remuneração e meses originais (antes de qualquer aditivo)
        # Para isso, vamos buscar o primeiro registro histórico ou usar uma lógica diferente
        # Por agora, vamos calcular baseado nos dados atuais e somar os aditivos
        
        # Primeiro, buscar os dados atuais do contrato
        cursor.execute(
            """
            SELECT remuneracao, meses
            FROM contrato_pf WHERE id=?
        """,
            (id_contrato,),
        )
        
        dados_atuais = cursor.fetchone()
        remuneracao_atual = float(dados_atuais[0]) if dados_atuais[0] else 0
        meses_atual = int(dados_atuais[1]) if dados_atuais[1] else 0
        
        # Calcular valor base atual (com remuneração e meses possivelmente já alterados por aditivos)
        total_base = (remuneracao_atual * meses_atual) + valor_intersticio + valor_complementar_original

        # Buscar e somar todos os valores dos aditivos
        cursor.execute(
            """
            SELECT COALESCE(SUM(valor_total_aditivo), 0)
            FROM aditivo_pf WHERE id_contrato=?
        """,
            (id_contrato,),
        )
        
        total_aditivos = cursor.fetchone()[0]
        total_aditivos = float(total_aditivos) if total_aditivos else 0

        # Total final do contrato = valor base + aditivos
        total_contrato = total_base + total_aditivos

        # Atualiza o contrato
        cursor.execute(
            """
            UPDATE contrato_pf SET total_contrato=? WHERE id=?
        """,
            (total_contrato, id_contrato),
        )

        conn.commit()

    conn.close()
