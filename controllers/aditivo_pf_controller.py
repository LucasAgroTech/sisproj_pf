# Aditivo Pf Controller.Py
from models.aditivo_pf_model import (
    create_aditivo_pf,
    get_all_aditivos_pf,
    get_aditivos_by_contrato,
    get_aditivo_by_id,
    update_aditivo_pf,
    delete_aditivo_pf,
)
from utils.session import Session
from utils.logger import log_action


def adicionar_aditivo(
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
    Adiciona um novo aditivo para contrato de pessoa física

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
    try:
        # Converter valores monetários para float
        if valor_aditivo:
            valor_aditivo = float(valor_aditivo)
        if nova_remuneracao:
            nova_remuneracao = float(nova_remuneracao)
        if diferenca_remuneracao:
            diferenca_remuneracao = float(diferenca_remuneracao)
        if valor_complementar:
            valor_complementar = float(valor_complementar)
        if valor_total_aditivo:
            valor_total_aditivo = float(valor_total_aditivo)

        # Converter meses para inteiro
        if meses:
            meses = int(meses)

        id_aditivo = create_aditivo_pf(
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
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(
                usuario[1], f"Cadastro de Aditivo PF para Contrato ID: {id_contrato}"
            )

        return id_aditivo

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao adicionar aditivo: {str(e)}")


def listar_aditivos():
    """
    Lista todos os aditivos

    Returns:
        list: Lista de aditivos
    """
    return get_all_aditivos_pf()


def listar_aditivos_por_contrato(id_contrato):
    """
    Lista os aditivos de um contrato específico

    Args:
        id_contrato (int): ID do contrato

    Returns:
        list: Lista de aditivos do contrato
    """
    return get_aditivos_by_contrato(id_contrato)


def buscar_aditivo_por_id(id_aditivo):
    """
    Busca um aditivo pelo ID

    Args:
        id_aditivo (int): ID do aditivo

    Returns:
        tuple: Dados do aditivo ou None
    """
    return get_aditivo_by_id(id_aditivo)


def editar_aditivo(
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
    Edita um aditivo

    Args:
        id_aditivo (int): ID do aditivo
        [outros parâmetros iguais ao adicionar_aditivo]
    """
    try:
        # Converter valores monetários para float
        if valor_aditivo:
            valor_aditivo = float(valor_aditivo)
        if nova_remuneracao:
            nova_remuneracao = float(nova_remuneracao)
        if diferenca_remuneracao:
            diferenca_remuneracao = float(diferenca_remuneracao)
        if valor_complementar:
            valor_complementar = float(valor_complementar)
        if valor_total_aditivo:
            valor_total_aditivo = float(valor_total_aditivo)

        # Converter meses para inteiro
        if meses:
            meses = int(meses)

        update_aditivo_pf(
            id_aditivo,
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
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Edição de Aditivo PF ID: {id_aditivo}")

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))


def excluir_aditivo(id_aditivo):
    """
    Exclui um aditivo

    Args:
        id_aditivo (int): ID do aditivo
    """
    try:
        delete_aditivo_pf(id_aditivo)

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Exclusão de Aditivo PF ID: {id_aditivo}")

    except ValueError as e:
        # Repassar a exceção para ser tratada na view
        raise ValueError(str(e))
