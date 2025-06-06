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
from utils.custeio_utils import CusteioManager

# Instância do CusteioManager para reutilização
custeio_manager = CusteioManager()


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
        # Converter valor para float de forma segura
        try:
            # Se valor for None, string vazia ou não numérico, usar 0
            valor_float = float(valor) if valor and str(valor).strip() else 0
        except ValueError:
            # Se não for possível converter para float, usar 0
            print(f"Erro ao processar produto: could not convert string to float: '{valor}'")
            valor_float = 0

        id_produto = create_produto_pf(
            id_contrato,
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor_float,
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
        # Converter valor para float de forma segura
        try:
            # Se valor for None, string vazia ou não numérico, usar 0
            valor_float = float(valor) if valor and str(valor).strip() else 0
        except ValueError:
            # Se não for possível converter para float, usar 0
            print(f"Erro ao processar produto: could not convert string to float: '{valor}'")
            valor_float = 0

        update_produto_pf(
            id_produto,
            numero,
            data_programada,
            instrumento,
            data_entrega,
            status,
            titulo,
            valor_float,
        )

        # Registrar a ação no log
        usuario = Session.get_user()
        if usuario:
            log_action(usuario[1], f"Edição de Produto ID: {id_produto}")

    except Exception as e:
        # Repassar a exceção para ser tratada na view
        raise Exception(f"Erro ao editar produto: {str(e)}")


def obter_proximo_numero_produto(id_contrato):
    """
    Obtém o próximo número sequencial para um produto do contrato

    Args:
        id_contrato (int): ID do contrato

    Returns:
        int: Próximo número sequencial para o produto
    """
    try:
        # Obter produtos do contrato
        produtos = get_produtos_by_contrato(id_contrato)
        
        # Se não houver produtos, retorna 1
        if not produtos:
            return 1
        
        # Tenta extrair o número de cada produto e encontrar o maior
        numeros = []
        for produto in produtos:
            numero_str = produto[2]  # Índice 2 é o campo 'numero'
            try:
                # Tenta converter para inteiro
                numero = int(numero_str)
                numeros.append(numero)
            except (ValueError, TypeError):
                # Se não for um número inteiro, ignora
                pass
        
        # Se não conseguiu extrair nenhum número válido, retorna 1
        if not numeros:
            return 1
        
        # Retorna o próximo número após o maior encontrado
        return max(numeros) + 1
        
    except Exception as e:
        # Em caso de erro, retorna 1 como valor padrão
        print(f"Erro ao obter próximo número de produto: {e}")
        return 1


def obter_instrumentos():
    """
    Obtém a lista de instrumentos únicos da tabela de custeio

    Returns:
        list: Lista de instrumentos únicos
    """
    try:
        # Obter instrumentos únicos da tabela de custeio (usando cod_projeto)
        instrumentos = custeio_manager.get_distinct_values('cod_projeto')
        return sorted(instrumentos) if instrumentos else []
    except Exception as e:
        print(f"Erro ao obter instrumentos: {e}")
        return []


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
