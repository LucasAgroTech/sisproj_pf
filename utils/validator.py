# Validator.Py
import re
from datetime import datetime


def validar_cpf(cpf):
    """
    Valida um CPF

    Args:
        cpf: CPF a ser validado (pode conter pontos e traço)

    Returns:
        bool: True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r"[^0-9]", "", cpf)

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    resto = soma % 11
    dv1 = 0 if resto < 2 else 11 - resto

    if dv1 != int(cpf[9]):
        return False

    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    resto = soma % 11
    dv2 = 0 if resto < 2 else 11 - resto

    if dv2 != int(cpf[10]):
        return False

    return True


def validar_email(email):
    """
    Valida um endereço de e-mail

    Args:
        email: E-mail a ser validado

    Returns:
        bool: True se o e-mail é válido, False caso contrário
    """
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email))


def validar_data(data, formato="%d/%m/%Y"):
    """
    Valida uma data no formato especificado

    Args:
        data: Data a ser validada
        formato: Formato da data (padrão: DD/MM/AAAA)

    Returns:
        bool: True se a data é válida, False caso contrário
    """
    try:
        datetime.strptime(data, formato)
        return True
    except ValueError:
        return False


def validar_periodo(data_inicial, data_final, formato="%d/%m/%Y"):
    """
    Valida se uma data final é posterior a uma data inicial

    Args:
        data_inicial: Data inicial
        data_final: Data final
        formato: Formato das datas (padrão: DD/MM/AAAA)

    Returns:
        bool: True se o período é válido, False caso contrário
    """
    try:
        data_ini = datetime.strptime(data_inicial, formato)
        data_fim = datetime.strptime(data_final, formato)
        return data_fim >= data_ini
    except ValueError:
        return False


def calcular_meses_entre_datas(data_inicial, data_final, formato="%d/%m/%Y"):
    """
    Calcula a quantidade de meses entre duas datas

    Args:
        data_inicial: Data inicial
        data_final: Data final
        formato: Formato das datas (padrão: DD/MM/AAAA)

    Returns:
        int: Quantidade de meses entre as datas
    """
    try:
        data_ini = datetime.strptime(data_inicial, formato)
        data_fim = datetime.strptime(data_final, formato)

        # Cálculo de meses
        meses = (data_fim.year - data_ini.year) * 12 + (data_fim.month - data_ini.month)

        # Ajusta considerando o dia do mês
        if data_fim.day < data_ini.day:
            meses -= 1

        return max(0, meses)
    except ValueError:
        return 0


def validar_telefone(telefone):
    """
    Valida um número de telefone brasileiro

    Args:
        telefone: Telefone a ser validado

    Returns:
        bool: True se o telefone é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    telefone = re.sub(r"[^0-9]", "", telefone)

    # Verifica se tem 10 ou 11 dígitos (com DDD)
    if len(telefone) not in [10, 11]:
        return False

    # Verifica se o DDD é válido (10 a 99)
    ddd = int(telefone[:2])
    if ddd < 10 or ddd > 99:
        return False

    return True


def formatar_cpf(cpf):
    """
    Formata um CPF no padrão XXX.XXX.XXX-XX

    Args:
        cpf: CPF a ser formatado

    Returns:
        str: CPF formatado
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r"[^0-9]", "", cpf)

    if len(cpf) != 11:
        return cpf

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_telefone(telefone):
    """
    Formata um telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX

    Args:
        telefone: Telefone a ser formatado

    Returns:
        str: Telefone formatado
    """
    # Remove caracteres não numéricos
    telefone = re.sub(r"[^0-9]", "", telefone)

    if len(telefone) == 11:  # Celular
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:  # Fixo
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        return telefone


def formatar_valor_monetario(valor, simbolo="R$"):
    """
    Formata um valor monetário no padrão R$ 0.000,00

    Args:
        valor: Valor a ser formatado
        simbolo: Símbolo da moeda (padrão: R$)

    Returns:
        str: Valor formatado
    """
    try:
        valor_float = float(valor)
        return (
            f"{simbolo} {valor_float:,.2f}".replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )
    except (ValueError, TypeError):
        return f"{simbolo} 0,00"


def calcular_total_contrato(
    remuneracao, meses, intersticio=False, valor_intersticio=0, valor_complementar=0
):
    """
    Calcula o valor total de um contrato

    Args:
        remuneracao: Valor da remuneração mensal
        meses: Quantidade de meses
        intersticio: Se possui interstício
        valor_intersticio: Valor do interstício
        valor_complementar: Valor complementar

    Returns:
        float: Valor total do contrato
    """
    try:
        remuneracao_float = float(remuneracao)
        meses_int = int(meses)
        valor_intersticio_float = float(valor_intersticio) if intersticio else 0
        valor_complementar_float = (
            float(valor_complementar) if valor_complementar else 0
        )

        return (
            (remuneracao_float * meses_int)
            + valor_intersticio_float
            + valor_complementar_float
        )
    except (ValueError, TypeError):
        return 0.0
