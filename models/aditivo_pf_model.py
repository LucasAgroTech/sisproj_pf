# Aditivo Pf Model.Py
from .db_manager import get_connection
from datetime import datetime


def create_aditivo_pf(
    id_contrato,
    tipo_aditivo,
    oficio=None,
    data_entrada=None,
    data_protocolo=None,
    instituicao=None,
    instrumento=None,
    subprojeto=None,
    ta=None,
    pta=None,
    acao=None,
    resultado=None,
    meta=None,
    vigencia_final=None,
    meses=None,
    valor_aditivo=0,
    vigencia_inicial=None,
    nova_remuneracao=None,
    diferenca_remuneracao=None,
    valor_complementar=None,
    valor_total_aditivo=None,
    responsavel=None,
):
    """
    Cria um novo aditivo para contrato de pessoa física

    Args:
        id_contrato (int): ID do contrato
        tipo_aditivo (str): Tipo do aditivo (prorrogacao, reajuste, ambos)
        oficio (str, optional): Número do ofício
        data_entrada (str, optional): Data de entrada
        data_protocolo (str, optional): Data de protocolo
        instituicao (str, optional): Instituição
        instrumento (str, optional): Instrumento
        subprojeto (str, optional): Subprojeto
        ta (str, optional): TA
        pta (str, optional): PTA
        acao (str, optional): Ação
        resultado (str, optional): Resultado
        meta (str, optional): Meta
        vigencia_final (str, optional): Nova data final de vigência
        meses (int, optional): Quantidade de meses
        valor_aditivo (float, optional): Valor do aditivo
        vigencia_inicial (str, optional): Data inicial de vigência
        nova_remuneracao (float, optional): Nova remuneração
        diferenca_remuneracao (float, optional): Diferença de remuneração
        valor_complementar (float, optional): Valor complementar
        valor_total_aditivo (float, optional): Valor total do aditivo
        responsavel (str, optional): Responsável pelo aditivo

    Returns:
        int: ID do aditivo criado
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Calcula o valor total do aditivo se não for fornecido
    if valor_total_aditivo is None:
        if tipo_aditivo == "prorrogacao" and meses and nova_remuneracao:
            # Para prorrogação, o valor total é o valor da nova remuneração * meses
            valor_total_aditivo = nova_remuneracao * meses
        elif tipo_aditivo == "reajuste" and diferenca_remuneracao:
            # Para reajuste, pegamos a diferença de remuneração
            cursor.execute("SELECT meses FROM contrato_pf WHERE id=?", (id_contrato,))
            contrato_meses = cursor.fetchone()
            if contrato_meses and contrato_meses[0]:
                valor_total_aditivo = diferenca_remuneracao * contrato_meses[0]
            else:
                valor_total_aditivo = diferenca_remuneracao
        else:
            # Para outros casos, usar o valor_aditivo
            valor_total_aditivo = valor_aditivo

    # Data de atualização atual
    data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO aditivo_pf (
            id_contrato, tipo_aditivo, oficio, data_entrada, data_protocolo,
            instituicao, instrumento, subprojeto, ta, pta, acao,
            resultado, meta, vigencia_final, meses, valor_aditivo,
            vigencia_inicial, nova_remuneracao, diferenca_remuneracao,
            valor_complementar, valor_total_aditivo, responsavel, data_atualizacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            id_contrato,
            tipo_aditivo,
            oficio,
            data_entrada,
            data_protocolo,
            instituicao,
            instrumento,
            subprojeto,
            ta,
            pta,
            acao,
            resultado,
            meta,
            vigencia_final,
            meses,
            valor_aditivo,
            vigencia_inicial,
            nova_remuneracao,
            diferenca_remuneracao,
            valor_complementar,
            valor_total_aditivo,
            responsavel,
            data_atualizacao,
        ),
    )

    # Obter o ID do aditivo inserido
    aditivo_id = cursor.lastrowid

    # Atualizar o contrato conforme o tipo de aditivo
    if tipo_aditivo == "prorrogacao" or tipo_aditivo == "ambos":
        # Atualizar a vigência final e meses no contrato
        if vigencia_final:
            cursor.execute(
                """
                UPDATE contrato_pf SET vigencia_final=?, meses=?
                WHERE id=?
            """,
                (vigencia_final, meses, id_contrato),
            )

    if tipo_aditivo == "reajuste" or tipo_aditivo == "ambos":
        # Atualizar a remuneração no contrato
        if nova_remuneracao:
            cursor.execute(
                """
                UPDATE contrato_pf SET remuneracao=?
                WHERE id=?
            """,
                (nova_remuneracao, id_contrato),
            )

    # Atualizar o valor total do contrato
    cursor.execute(
        """
        UPDATE contrato_pf SET total_contrato = total_contrato + ?
        WHERE id=?
    """,
        (valor_total_aditivo, id_contrato),
    )

    conn.commit()
    conn.close()

    return aditivo_id


def get_all_aditivos_pf():
    """
    Retorna todos os aditivos de contratos PF

    Returns:
        list: Lista de tuplas com os aditivos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, c.numero_contrato, p.nome_completo
        FROM aditivo_pf a
        JOIN contrato_pf c ON a.id_contrato = c.id
        JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
        ORDER BY a.id DESC
    """
    )
    aditivos = cursor.fetchall()
    conn.close()

    return [tuple(aditivo) for aditivo in aditivos]


def get_aditivos_by_contrato(id_contrato):
    """
    Retorna os aditivos de um contrato específico

    Args:
        id_contrato (int): ID do contrato

    Returns:
        list: Lista de tuplas com os aditivos
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, c.numero_contrato, p.nome_completo
        FROM aditivo_pf a
        JOIN contrato_pf c ON a.id_contrato = c.id
        JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
        WHERE a.id_contrato = ?
        ORDER BY a.id ASC
    """,
        (id_contrato,),
    )
    aditivos = cursor.fetchall()
    conn.close()

    return [tuple(aditivo) for aditivo in aditivos]


def get_aditivo_by_id(id_aditivo):
    """
    Obtém um aditivo pelo seu ID

    Args:
        id_aditivo (int): ID do aditivo

    Returns:
        tuple: Dados do aditivo ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT a.*, c.numero_contrato, p.nome_completo
        FROM aditivo_pf a
        JOIN contrato_pf c ON a.id_contrato = c.id
        JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
        WHERE a.id = ?
    """,
        (id_aditivo,),
    )
    aditivo = cursor.fetchone()
    conn.close()

    if aditivo:
        return tuple(aditivo)
    return None


def update_aditivo_pf(
    id_aditivo,
    tipo_aditivo,
    oficio=None,
    data_entrada=None,
    data_protocolo=None,
    instituicao=None,
    instrumento=None,
    subprojeto=None,
    ta=None,
    pta=None,
    acao=None,
    resultado=None,
    meta=None,
    vigencia_final=None,
    meses=None,
    valor_aditivo=0,
    vigencia_inicial=None,
    nova_remuneracao=None,
    diferenca_remuneracao=None,
    valor_complementar=None,
    valor_total_aditivo=None,
    responsavel=None,
):
    """
    Atualiza um aditivo de contrato PF

    Args:
        id_aditivo (int): ID do aditivo
        [outros parâmetros iguais ao create_aditivo_pf]
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Obter dados atuais do aditivo
    cursor.execute(
        "SELECT id_contrato, valor_total_aditivo FROM aditivo_pf WHERE id=?",
        (id_aditivo,),
    )
    aditivo_atual = cursor.fetchone()

    if not aditivo_atual:
        conn.close()
        raise ValueError(f"Aditivo com ID {id_aditivo} não encontrado")

    id_contrato = aditivo_atual[0]
    valor_total_anterior = float(aditivo_atual[1]) if aditivo_atual[1] else 0

    # Calcular o novo valor total do aditivo se não for fornecido
    if valor_total_aditivo is None:
        if tipo_aditivo == "prorrogacao" and meses and nova_remuneracao:
            valor_total_aditivo = nova_remuneracao * meses
        elif tipo_aditivo == "reajuste" and diferenca_remuneracao:
            cursor.execute("SELECT meses FROM contrato_pf WHERE id=?", (id_contrato,))
            contrato_meses = cursor.fetchone()
            if contrato_meses and contrato_meses[0]:
                valor_total_aditivo = diferenca_remuneracao * contrato_meses[0]
            else:
                valor_total_aditivo = diferenca_remuneracao
        else:
            valor_total_aditivo = valor_aditivo

    # Data de atualização atual
    data_atualizacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Atualizar o aditivo
    cursor.execute(
        """
        UPDATE aditivo_pf SET
            tipo_aditivo=?, oficio=?, data_entrada=?, data_protocolo=?,
            instituicao=?, instrumento=?, subprojeto=?, ta=?, pta=?, acao=?,
            resultado=?, meta=?, vigencia_final=?, meses=?, valor_aditivo=?,
            vigencia_inicial=?, nova_remuneracao=?, diferenca_remuneracao=?,
            valor_complementar=?, valor_total_aditivo=?, responsavel=?, data_atualizacao=?
        WHERE id=?
    """,
        (
            tipo_aditivo,
            oficio,
            data_entrada,
            data_protocolo,
            instituicao,
            instrumento,
            subprojeto,
            ta,
            pta,
            acao,
            resultado,
            meta,
            vigencia_final,
            meses,
            valor_aditivo,
            vigencia_inicial,
            nova_remuneracao,
            diferenca_remuneracao,
            valor_complementar,
            valor_total_aditivo,
            responsavel,
            data_atualizacao,
            id_aditivo,
        ),
    )

    # Atualizar o contrato conforme o tipo de aditivo
    if tipo_aditivo == "prorrogacao" or tipo_aditivo == "ambos":
        # Atualizar a vigência final e meses no contrato
        if vigencia_final:
            cursor.execute(
                """
                UPDATE contrato_pf SET vigencia_final=?, meses=?
                WHERE id=?
            """,
                (vigencia_final, meses, id_contrato),
            )

    if tipo_aditivo == "reajuste" or tipo_aditivo == "ambos":
        # Atualizar a remuneração no contrato
        if nova_remuneracao:
            cursor.execute(
                """
                UPDATE contrato_pf SET remuneracao=?
                WHERE id=?
            """,
                (nova_remuneracao, id_contrato),
            )

    # Atualizar o valor total do contrato considerando a diferença
    diferenca_valor = float(valor_total_aditivo) - valor_total_anterior
    cursor.execute(
        """
        UPDATE contrato_pf SET total_contrato = total_contrato + ?
        WHERE id=?
    """,
        (diferenca_valor, id_contrato),
    )

    conn.commit()
    conn.close()


def delete_aditivo_pf(id_aditivo):
    """
    Exclui um aditivo de contrato PF

    Args:
        id_aditivo (int): ID do aditivo

    Raises:
        ValueError: Se não for o último aditivo do contrato
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Obter dados do aditivo
    cursor.execute(
        "SELECT id_contrato, valor_total_aditivo FROM aditivo_pf WHERE id=?",
        (id_aditivo,),
    )
    aditivo = cursor.fetchone()

    if not aditivo:
        conn.close()
        raise ValueError(f"Aditivo com ID {id_aditivo} não encontrado")

    id_contrato = aditivo[0]
    valor_aditivo = float(aditivo[1]) if aditivo[1] else 0

    # Verificar se é o último aditivo do contrato
    cursor.execute(
        """
        SELECT id FROM aditivo_pf 
        WHERE id_contrato=? 
        ORDER BY id DESC 
        LIMIT 1
    """,
        (id_contrato,),
    )

    ultimo_aditivo = cursor.fetchone()

    if not ultimo_aditivo or ultimo_aditivo[0] != id_aditivo:
        conn.close()
        raise ValueError("Somente o último aditivo pode ser excluído")

    # Excluir o aditivo
    cursor.execute("DELETE FROM aditivo_pf WHERE id=?", (id_aditivo,))

    # Atualizar o valor total do contrato
    cursor.execute(
        """
        UPDATE contrato_pf SET total_contrato = total_contrato - ?
        WHERE id=?
    """,
        (valor_aditivo, id_contrato),
    )

    conn.commit()
    conn.close()
