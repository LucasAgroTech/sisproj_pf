# Contrato Pf Controller.Py
from models.contrato_pf_model import (
    create_contrato_pf,
    get_all_contratos_pf,
    get_contratos_by_pessoa,
    get_contratos_by_demanda,
    get_contrato_by_id,
    update_contrato_pf,
    delete_contrato_pf,
    search_contratos_pf,
    update_total_contrato,
)
from models.db_manager_access import get_connection
from utils.session import Session
from utils.logger import log_action


def adicionar_contrato(
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
):
    """
    Adiciona um novo contrato de pessoa física

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
        modalidade (str): Modalidade do contrato
        natureza_demanda (str): Natureza da demanda
        numero_contrato (str): Número do contrato
        vigencia_inicial (str): Data de início da vigência
        vigencia_final (str): Data de fim da vigência
        meses (int): Quantidade de meses
        status_contrato (str): Status do contrato
        remuneracao (float): Valor da remuneração
        intersticio (int): Se tem interstício (0 ou 1)
        valor_intersticio (float): Valor do interstício
        valor_complementar (float): Valor complementar
        total_contrato (float): Valor total do contrato
        observacoes (str): Observações
        lotacao (str): Lotação
        exercicio (str): Exercício

    Returns:
        int: ID do contrato adicionado
    """
    try:
        try:
            # Converte o interstício para inteiro (0 ou 1)
            intersticio_int = 1 if intersticio else 0

            # Converte valores monetários para float
            remuneracao_float = float(remuneracao) if remuneracao else 0
            valor_intersticio_float = (
                float(valor_intersticio) if valor_intersticio and intersticio_int else 0
            )
            valor_complementar_float = (
                float(valor_complementar) if valor_complementar else 0
            )

            # Calcula o total do contrato se não for fornecido
            if not total_contrato:
                total_contrato = (
                    (remuneracao_float * int(meses))
                    + valor_intersticio_float
                    + valor_complementar_float
                )
        except Exception as e:
            raise Exception(f"Erro ao calcular total: {str(e)}")

        id_contrato = create_contrato_pf(
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
            remuneracao_float,
            intersticio_int,
            valor_intersticio_float,
            valor_complementar_float,
            total_contrato,
            observacoes,
            lotacao,
            exercicio,
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1],
                f"Cadastro de Contrato PF: {numero_contrato} (ID: {id_contrato})",
            )

        return id_contrato

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao adicionar contrato: {str(e)}")


def listar_contratos():
    """
    Lista todos os contratos

    Returns:
        list: Lista de tuplas com os contratos
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Buscar contratos com nome da pessoa
        cursor.execute(
            """
            SELECT c.id, c.codigo_demanda, c.id_pessoa_fisica, c.instituicao, c.instrumento, 
                   c.subprojeto, c.ta, c.pta, c.acao, c.resultado, c.meta, c.modalidade, 
                   c.natureza_demanda, c.numero_contrato, c.vigencia_inicial, c.vigencia_final, 
                   c.meses, c.status_contrato, c.remuneracao, c.intersticio, c.valor_intersticio, 
                   c.valor_complementar, c.total_contrato, c.observacoes, c.lotacao, c.exercicio,
                   p.nome_completo
            FROM contrato_pf c
            LEFT JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
            ORDER BY c.id DESC
            """
        )
        contratos = cursor.fetchall()

        # Converter para lista para poder modificar
        contratos = [list(contrato) for contrato in contratos]

        # Formatar valores monetários
        for contrato in contratos:
            if contrato[18] is not None:  # remuneracao
                contrato[18] = float(contrato[18])
            if contrato[20] is not None:  # valor_intersticio
                contrato[20] = float(contrato[20])
            if contrato[21] is not None:  # valor_complementar
                contrato[21] = float(contrato[21])
            if contrato[22] is not None:  # total_contrato
                contrato[22] = float(contrato[22])

        return contratos

    except Exception as e:
        raise Exception(f"Erro ao listar contratos: {str(e)}")
    finally:
        conn.close()


def listar_contratos_por_pessoa(id_pessoa_fisica):
    """
    Lista os contratos de uma pessoa física específica

    Args:
        id_pessoa_fisica (int): ID da pessoa física

    Returns:
        list: Lista de contratos da pessoa
    """
    return get_contratos_by_pessoa(id_pessoa_fisica)


def listar_contratos_por_demanda(codigo_demanda):
    """
    Lista os contratos vinculados a uma demanda específica

    Args:
        codigo_demanda (int): Código da demanda

    Returns:
        list: Lista de contratos da demanda
    """
    return get_contratos_by_demanda(codigo_demanda)


def buscar_contrato_por_id(id_contrato):
    """
    Busca um contrato pelo ID

    Args:
        id_contrato (int): ID do contrato

    Returns:
        tuple: Dados do contrato ou None se não encontrado
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Buscar contrato com nome da pessoa
        cursor.execute(
            """
            SELECT c.id, c.codigo_demanda, c.id_pessoa_fisica, c.instituicao, c.instrumento, 
                   c.subprojeto, c.ta, c.pta, c.acao, c.resultado, c.meta, c.modalidade, 
                   c.natureza_demanda, c.numero_contrato, c.vigencia_inicial, c.vigencia_final, 
                   c.meses, c.status_contrato, c.remuneracao, c.intersticio, c.valor_intersticio, 
                   c.valor_complementar, c.total_contrato, c.observacoes, c.lotacao, c.exercicio,
                   p.nome_completo
            FROM contrato_pf c
            LEFT JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
            WHERE c.id = ?
            """,
            (id_contrato,),
        )
        contrato = cursor.fetchone()

        if contrato:
            # Converter para lista para poder modificar
            contrato = list(contrato)
            
            # Formatar valores monetários
            if contrato[18] is not None:  # remuneracao
                contrato[18] = float(contrato[18])
            if contrato[20] is not None:  # valor_intersticio
                contrato[20] = float(contrato[20])
            if contrato[21] is not None:  # valor_complementar
                contrato[21] = float(contrato[21])
            if contrato[22] is not None:  # total_contrato
                contrato[22] = float(contrato[22])

        return contrato

    except Exception as e:
        raise Exception(f"Erro ao buscar contrato: {str(e)}")
    finally:
        conn.close()


def editar_contrato(
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
    valor_intersticio,
    valor_complementar,
    total_contrato,
    observacoes,
    lotacao,
    exercicio,
):
    """
    Edita um contrato de pessoa física existente

    Args:
        id_contrato (int): ID do contrato a ser editado
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
        modalidade (str): Modalidade do contrato
        natureza_demanda (str): Natureza da demanda
        numero_contrato (str): Número do contrato
        vigencia_inicial (str): Data de início da vigência
        vigencia_final (str): Data de fim da vigência
        meses (int): Quantidade de meses
        status_contrato (str): Status do contrato
        remuneracao (float): Valor da remuneração
        intersticio (int): Se tem interstício (0 ou 1)
        valor_intersticio (float): Valor do interstício
        valor_complementar (float): Valor complementar
        total_contrato (float): Valor total do contrato
        observacoes (str): Observações
        lotacao (str): Lotação
        exercicio (str): Exercício

    Returns:
        bool: True se a edição foi bem sucedida
    """
    try:
        try:
            # Converte o interstício para inteiro (0 ou 1)
            intersticio_int = 1 if intersticio else 0

            # Converte valores monetários para float
            remuneracao_float = float(remuneracao) if remuneracao else 0
            valor_intersticio_float = (
                float(valor_intersticio) if valor_intersticio and intersticio_int else 0
            )
            valor_complementar_float = (
                float(valor_complementar) if valor_complementar else 0
            )

            # Calcula o total do contrato se não for fornecido
            if not total_contrato:
                total_contrato = (
                    (remuneracao_float * int(meses))
                    + valor_intersticio_float
                    + valor_complementar_float
                )
        except Exception as e:
            raise Exception(f"Erro ao calcular total: {str(e)}")

        update_contrato_pf(
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
            remuneracao_float,
            intersticio_int,
            valor_intersticio_float,
            valor_complementar_float,
            total_contrato,
            observacoes,
            lotacao,
            exercicio,
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1],
                f"Edição de Contrato PF: {numero_contrato} (ID: {id_contrato})",
            )

        return True

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao editar contrato: {str(e)}")


def excluir_contrato(id_contrato):
    """
    Exclui um contrato de pessoa física

    Args:
        id_contrato (int): ID do contrato
    """
    try:
        # Buscar o número do contrato antes de excluir (para o log)
        contrato = get_contrato_by_id(id_contrato)
        numero_contrato = (
            contrato[13] if contrato and len(contrato) > 13 else f"ID: {id_contrato}"
        )

        delete_contrato_pf(id_contrato)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Exclusão de Contrato PF: {numero_contrato}")

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))


def buscar_contratos(termo_busca):
    """
    Busca contratos por número, nome da pessoa ou modalidade

    Args:
        termo_busca (str): Termo para busca

    Returns:
        list: Lista de contratos encontrados
    """
    return search_contratos_pf(termo_busca)


def atualizar_total_contrato(id_contrato):
    """
    Recalcula e atualiza o valor total do contrato

    Args:
        id_contrato (int): ID do contrato
    """
    update_total_contrato(id_contrato)

    # Registrar a ação no log
    usuario = Session.get_user()
    if usuario:
        log_action(
            usuario[1], f"Atualização de valor total do Contrato PF (ID: {id_contrato})"
        )
