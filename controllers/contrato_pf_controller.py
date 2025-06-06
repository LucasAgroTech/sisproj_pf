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
    valor_intersticio=0,
    valor_complementar=0,
    total_contrato=0,
    observacoes=None,
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

    Returns:
        int: ID do contrato criado
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
    Lista todos os contratos de pessoa física

    Returns:
        list: Lista de contratos
    """
    return get_all_contratos_pf()


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
        tuple: Dados do contrato ou None
    """
    return get_contrato_by_id(id_contrato)


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
    valor_intersticio=0,
    valor_complementar=0,
    total_contrato=0,
    observacoes=None,
):
    """
    Edita um contrato de pessoa física

    Args:
        id_contrato (int): ID do contrato
        [outros parâmetros iguais ao adicionar_contrato]
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
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1],
                f"Edição de Contrato PF: {numero_contrato} (ID: {id_contrato})",
            )

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
