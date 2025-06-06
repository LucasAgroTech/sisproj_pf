# Contrato Pf View.Py
import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime

from controllers.contrato_pf_controller import (
    adicionar_contrato,
    listar_contratos,
    buscar_contrato_por_id,
    editar_contrato,
    excluir_contrato,
    buscar_contratos,
    atualizar_total_contrato,
)
from controllers.pessoa_fisica_controller import listar_pessoas, buscar_pessoa_por_id
from controllers.demanda_controller import (
    adicionar_demanda,
    listar_demandas,
    buscar_demanda_por_id,
)
from controllers.aditivo_pf_controller import (
    listar_aditivos_por_contrato,
    adicionar_aditivo,
    excluir_aditivo,
)
from controllers.produto_pf_controller import (
    listar_produtos_por_contrato,
    adicionar_produto,
    excluir_produto,
    buscar_produto_por_id,
)
from utils.ui_utils import (
    FormularioBase,
    TabelaBase,
    criar_botao,
    mostrar_mensagem,
    Estilos,
    Cores,
    formatar_data,
    formatar_valor_brl,
    validar_numerico,
    converter_valor_brl_para_float,
)
from utils.validator import (
    validar_data,
    validar_periodo,
    calcular_meses_entre_datas,
    calcular_total_contrato,
)


class ContratoPFForm(FormularioBase):
    """Formulário para cadastro e edição de contratos de pessoa física"""

    def __init__(self, master, callback_salvar, callback_cancelar, contrato=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            contrato: dados do contrato para edição (opcional)
        """
        super().__init__(
            master, "Cadastro de Contrato" if not contrato else "Edição de Contrato"
        )

        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.contrato = contrato
        self.id_contrato = contrato[0] if contrato else None
        self.modo_edicao = contrato is not None

        # Frame principal para organizar o layout
        self.frame_principal = ttk.Frame(self)
        self.frame_principal.pack(
            fill=tk.BOTH, expand=True, pady=(0, 60)
        )  # Deixa espaço para os botões

        # Notebook para organizar os campos em abas
        self.notebook = ttk.Notebook(self.frame_principal)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Botões de ação (criados por último para garantir que fiquem visíveis)
        self.frame_botoes = ttk.Frame(self)
        self.frame_botoes.pack(fill=tk.X, pady=10, side=tk.BOTTOM, anchor=tk.S)

        self.btn_cancelar = criar_botao(
            self.frame_botoes, "Cancelar", self.cancelar, "Secundario", 15
        )
        self.btn_cancelar.pack(side=tk.RIGHT, padx=5)

        self.btn_salvar = criar_botao(
            self.frame_botoes, "Salvar", self.salvar, "Primario", 15
        )
        self.btn_salvar.pack(side=tk.RIGHT)

        # Aba de pessoa física (primeira aba)
        self.tab_pessoa = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pessoa, text="Pessoa Física")

        # Configurar campos na aba de pessoa física
        self.form_pessoa = FormularioBase(self.tab_pessoa, "")
        self.form_pessoa.pack(fill=tk.BOTH, expand=True)

        # Campo para seleção da pessoa física
        # Frame para a seleção da pessoa
        frame_pessoa = ttk.Frame(self.form_pessoa)
        frame_pessoa.pack(fill=tk.X, pady=5)

        ttk.Label(frame_pessoa, text="Pessoa Física*:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )

        # Frame para combobox e botão de busca
        frame_combo_pessoa = ttk.Frame(frame_pessoa)
        frame_combo_pessoa.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Combobox para seleção da pessoa
        self.pessoa_var = tk.StringVar()
        self.pessoa_combobox = ttk.Combobox(
            frame_combo_pessoa, textvariable=self.pessoa_var, width=40
        )
        self.pessoa_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botão de busca de pessoa
        btn_buscar_pessoa = tk.Button(
            frame_combo_pessoa,
            text="🔍",
            command=self.buscar_pessoa,
            bg=Cores.BACKGROUND_CLARO,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
        )
        btn_buscar_pessoa.pack(side=tk.RIGHT, padx=(2, 0))

        # Carregar pessoas físicas para o combobox
        self.carregar_pessoas()

        # Campo oculto para armazenar o ID da pessoa selecionada
        self.id_pessoa_selecionada = tk.StringVar()

        # Vincular evento de seleção do combobox
        self.pessoa_combobox.bind("<<ComboboxSelected>>", self.selecionar_pessoa)

        # Mostrar os dados da pessoa selecionada
        frame_info_pessoa = ttk.Frame(self.form_pessoa)
        frame_info_pessoa.pack(fill=tk.X, pady=5)

        ttk.Label(frame_info_pessoa, text="Informações:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )
        self.info_pessoa_label = ttk.Label(
            frame_info_pessoa, text="Nenhuma pessoa selecionada", foreground="gray"
        )
        self.info_pessoa_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Se for edição, selecionar a pessoa do contrato
        if self.modo_edicao and contrato:
            id_pessoa = contrato[2]  # ID da pessoa física
            pessoa = buscar_pessoa_por_id(id_pessoa)
            if pessoa:
                self.id_pessoa_selecionada.set(str(pessoa[0]))
                self.pessoa_var.set(pessoa[1])  # Nome completo
                self.atualizar_info_pessoa(pessoa)

        # Aba de demanda (segunda aba)
        self.tab_demanda = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_demanda, text="Demanda")

        # Configurar campos na aba de demanda
        self.form_demanda = FormularioBase(self.tab_demanda, "")
        self.form_demanda.pack(fill=tk.BOTH, expand=True)

        if not self.modo_edicao:
            # Para novos cadastros, não mostramos o código (será automático)
            self.form_demanda.adicionar_campo(
                "data_entrada", "Data de Entrada", tipo="data", padrao="", required=True
            )
            # Configurar formatação para data de entrada
            data_entrada_widget = self.form_demanda.campos["data_entrada"]["widget"]
            data_entrada_widget.bind(
                "<KeyRelease>", lambda e: formatar_data(data_entrada_widget, e)
            )
            data_entrada_widget.bind("<KeyPress>", validar_numerico)

            self.form_demanda.adicionar_campo(
                "data_protocolo", "Data de Protocolo", tipo="data", padrao=""
            )
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind(
                "<KeyRelease>", lambda e: formatar_data(data_protocolo_widget, e)
            )
            data_protocolo_widget.bind("<KeyPress>", validar_numerico)

            self.form_demanda.adicionar_campo("nup_sei", "NUP/SEI", padrao="")

            self.form_demanda.adicionar_campo("oficio", "Ofício", padrao="")

            # Lista de solicitantes
            solicitantes_opcoes = [
                "AECI/MS",
                "AISA/MS",
                "APSD/MS",
                "ASCOM/MS",
                "ASPAR/MS",
                "AUDSUS/MS",
                "CGARTI/SECTICS/MS",
                "CGOEX/SECTICS/MS",
                "CGPO/SECTICS/MS",
                "CGPROJ/SECTICS/MS",
                "CMED/ANVISA",
                "CONJUR/MS",
                "CORREGEDORIA/MS",
                "DAF/SECTICS/MS",
                "DECEIIS/SECTICS/MS",
                "DECIT/SECTICS/MS",
                "DESID/SECTICS/MS",
                "DGITS/SECTICS/MS",
                "GABINETE/SECTICS/MS",
                "GM/MS",
                "OUVSUS/MS",
                "SAES/MS",
                "SAPS/MS",
                "SE/MS",
                "SEIDIGI/MS",
                "SESAI/MS",
                "SGTES/MS",
                "SVSA/MS",
            ]
            self.form_demanda.adicionar_campo(
                "solicitante",
                "Solicitante",
                tipo="opcoes",
                opcoes=solicitantes_opcoes,
                padrao=solicitantes_opcoes[0] if solicitantes_opcoes else "",
                required=True,
            )

            status_opcoes = [
                "Novo",
                "Em Análise",
                "Aprovado",
                "Reprovado",
                "Concluído",
                "Cancelado",
            ]
            self.form_demanda.adicionar_campo(
                "status",
                "Status",
                tipo="opcoes",
                opcoes=status_opcoes,
                padrao="Novo",
                required=True,
            )
        else:
            # Para edição, buscamos os dados da demanda pelo código
            codigo_demanda = contrato[1]
            demanda_encontrada = buscar_demanda_por_id(codigo_demanda)

            # Para edição, mostramos o código da demanda
            self.form_demanda.adicionar_campo(
                "codigo_demanda",
                "Código da Demanda",
                padrao=str(codigo_demanda),
                required=False,
            )

            # Adicionar campos com os dados da demanda encontrada
            data_entrada_valor = demanda_encontrada[1] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo(
                "data_entrada",
                "Data de Entrada",
                tipo="data",
                padrao=data_entrada_valor,
                required=True,
            )
            # Configurar formatação para data de entrada
            data_entrada_widget = self.form_demanda.campos["data_entrada"]["widget"]
            data_entrada_widget.bind(
                "<KeyRelease>", lambda e: formatar_data(data_entrada_widget, e)
            )
            data_entrada_widget.bind("<KeyPress>", validar_numerico)

            data_protocolo_valor = demanda_encontrada[3] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo(
                "data_protocolo",
                "Data de Protocolo",
                tipo="data",
                padrao=data_protocolo_valor,
            )
            # Configurar formatação para data de protocolo
            data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
            data_protocolo_widget.bind(
                "<KeyRelease>", lambda e: formatar_data(data_protocolo_widget, e)
            )
            data_protocolo_widget.bind("<KeyPress>", validar_numerico)

            nup_sei_valor = demanda_encontrada[5] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo(
                "nup_sei", "NUP/SEI", padrao=nup_sei_valor
            )

            oficio_valor = demanda_encontrada[4] if demanda_encontrada else ""
            self.form_demanda.adicionar_campo("oficio", "Ofício", padrao=oficio_valor)

            # Lista de solicitantes
            solicitantes_opcoes = [
                "AECI/MS",
                "AISA/MS",
                "APSD/MS",
                "ASCOM/MS",
                "ASPAR/MS",
                "AUDSUS/MS",
                "CGARTI/SECTICS/MS",
                "CGOEX/SECTICS/MS",
                "CGPO/SECTICS/MS",
                "CGPROJ/SECTICS/MS",
                "CMED/ANVISA",
                "CONJUR/MS",
                "CORREGEDORIA/MS",
                "DAF/SECTICS/MS",
                "DECEIIS/SECTICS/MS",
                "DECIT/SECTICS/MS",
                "DESID/SECTICS/MS",
                "DGITS/SECTICS/MS",
                "GABINETE/SECTICS/MS",
                "GM/MS",
                "OUVSUS/MS",
                "SAES/MS",
                "SAPS/MS",
                "SE/MS",
                "SEIDIGI/MS",
                "SESAI/MS",
                "SGTES/MS",
                "SVSA/MS",
            ]

            # Adicionar campo de solicitante com valor padrão
            solicitante_valor = (
                demanda_encontrada[2] if demanda_encontrada else solicitantes_opcoes[0]
            )
            self.form_demanda.adicionar_campo(
                "solicitante",
                "Solicitante",
                tipo="opcoes",
                opcoes=solicitantes_opcoes,
                padrao=solicitante_valor,
                required=True,
            )

            # Adicionar campo de status
            status_opcoes = [
                "Novo",
                "Em Análise",
                "Aprovado",
                "Reprovado",
                "Concluído",
                "Cancelado",
            ]

            # Adicionar campo de status com valor padrão
            status_valor = (
                demanda_encontrada[6]
                if demanda_encontrada and len(demanda_encontrada) > 6
                else "Novo"
            )
            self.form_demanda.adicionar_campo(
                "status",
                "Status",
                tipo="opcoes",
                opcoes=status_opcoes,
                padrao=status_valor,
                required=True,
            )

        # Aba de custeio (terceira aba)
        self.tab_custeio = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_custeio, text="Custeio")

        # Configurar campos na aba de custeio
        self.form_custeio = FormularioBase(self.tab_custeio, "")
        self.form_custeio.pack(fill=tk.BOTH, expand=True)

        # Opções para instituição
        instituicoes_opcoes = ["OPAS", "FIOCRUZ"]

        # Garantir que a instituição seja uma das opções válidas
        instituicao_padrao = ""
        if contrato and len(contrato) > 3 and contrato[3]:
            if contrato[3] in instituicoes_opcoes:
                instituicao_padrao = contrato[3]
            else:
                instituicao_padrao = instituicoes_opcoes[0]
        else:
            instituicao_padrao = instituicoes_opcoes[0]

        self.form_custeio.adicionar_campo(
            "instituicao",
            "Instituição",
            tipo="opcoes",
            opcoes=instituicoes_opcoes,
            padrao=instituicao_padrao,
            required=True,
        )

        # Inicialmente, adicionamos opções vazias para evitar erro
        self.form_custeio.adicionar_campo(
            "instrumento",
            "Instrumento",
            tipo="opcoes",
            opcoes=["TC 132", "TC 145", "TC 150"],
            padrao=contrato[4] if contrato and len(contrato) > 4 else "",
        )

        self.form_custeio.adicionar_campo(
            "subprojeto",
            "Subprojeto",
            tipo="opcoes",
            opcoes=["SP 1", "SP 2", "SP 3"],
            padrao=contrato[5] if contrato and len(contrato) > 5 else "",
        )

        self.form_custeio.adicionar_campo(
            "ta",
            "TA",
            tipo="opcoes",
            opcoes=["1TA", "2TA", "3TA"],
            padrao=contrato[6] if contrato and len(contrato) > 6 else "",
        )

        self.form_custeio.adicionar_campo(
            "pta",
            "PTA",
            tipo="opcoes",
            opcoes=["2022", "2023", "2024", "2025"],
            padrao=contrato[7] if contrato and len(contrato) > 7 else "",
        )

        self.form_custeio.adicionar_campo(
            "acao",
            "Ação",
            tipo="opcoes",
            opcoes=["01", "02", "03", "04", "05"],
            padrao=contrato[8] if contrato and len(contrato) > 8 else "",
        )

        self.form_custeio.adicionar_campo(
            "resultado",
            "Resultado",
            tipo="opcoes",
            opcoes=["RE 01", "RE 02", "RE 03"],
            padrao=contrato[9] if contrato and len(contrato) > 9 else "",
        )

        self.form_custeio.adicionar_campo(
            "meta",
            "Meta",
            tipo="opcoes",
            opcoes=["Meta 1", "Meta 2", "Meta 3"],
            padrao=contrato[10] if contrato and len(contrato) > 10 else "",
        )

        # Aba de contrato (quarta aba)
        self.tab_contrato = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_contrato, text="Contrato")

        # Configurar campos na aba de contrato
        self.form_contrato = FormularioBase(self.tab_contrato, "")
        self.form_contrato.pack(fill=tk.BOTH, expand=True)

        # Modalidade do contrato
        modalidades_opcoes = ["BOLSA", "PRODUTO", "RPA", "CLT"]
        modalidade_padrao = contrato[11] if contrato and len(contrato) > 11 else "BOLSA"
        self.form_contrato.adicionar_campo(
            "modalidade",
            "Modalidade",
            tipo="opcoes",
            opcoes=modalidades_opcoes,
            padrao=modalidade_padrao,
            required=True,
        )

        # Natureza da demanda
        naturezas_opcoes = ["novo", "renovacao"]
        natureza_padrao = contrato[12] if contrato and len(contrato) > 12 else "novo"
        self.form_contrato.adicionar_campo(
            "natureza_demanda",
            "Natureza da Demanda",
            tipo="opcoes",
            opcoes=naturezas_opcoes,
            padrao=natureza_padrao,
            required=True,
        )

        # Número do contrato
        self.form_contrato.adicionar_campo(
            "numero_contrato",
            "Número do Contrato",
            padrao=contrato[13] if contrato and len(contrato) > 13 else "",
            required=True,
        )

        # Vigência inicial
        self.form_contrato.adicionar_campo(
            "vigencia_inicial",
            "Vigência Inicial",
            tipo="data",
            padrao=contrato[14] if contrato and len(contrato) > 14 else "",
            required=True,
        )
        # Configurar formatação para vigência inicial
        vigencia_inicial_widget = self.form_contrato.campos["vigencia_inicial"][
            "widget"
        ]
        vigencia_inicial_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(vigencia_inicial_widget, e)
        )
        vigencia_inicial_widget.bind("<FocusOut>", self.calcular_meses)

        # Vigência final
        self.form_contrato.adicionar_campo(
            "vigencia_final",
            "Vigência Final",
            tipo="data",
            padrao=contrato[15] if contrato and len(contrato) > 15 else "",
            required=True,
        )
        # Configurar formatação para vigência final
        vigencia_final_widget = self.form_contrato.campos["vigencia_final"]["widget"]
        vigencia_final_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(vigencia_final_widget, e)
        )
        vigencia_final_widget.bind("<FocusOut>", self.calcular_meses)

        # Meses
        meses_padrao = contrato[16] if contrato and len(contrato) > 16 else ""
        self.form_contrato.adicionar_campo(
            "meses", "Meses", tipo="numero", padrao=meses_padrao, required=True
        )

        # Status do contrato
        status_opcoes = [
            "pendente_assinatura",
            "cancelado",
            "concluido",
            "em_tramitacao",
            "aguardando_autorizacao",
            "nao_autorizado",
            "rescindido",
            "vigente",
        ]
        status_padrao = (
            contrato[17] if contrato and len(contrato) > 17 else "pendente_assinatura"
        )
        self.form_contrato.adicionar_campo(
            "status_contrato",
            "Status do Contrato",
            tipo="opcoes",
            opcoes=status_opcoes,
            padrao=status_padrao,
            required=True,
        )

        # Remuneração
        remuneracao_padrao = contrato[18] if contrato and len(contrato) > 18 else ""
        self.form_contrato.adicionar_campo(
            "remuneracao",
            "Remuneração",
            tipo="numero",
            padrao=remuneracao_padrao,
            required=True,
        )
        # Configurar formatação para remuneração
        remuneracao_widget = self.form_contrato.campos["remuneracao"]["widget"]
        remuneracao_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(remuneracao_widget, e)
        )
        remuneracao_widget.bind("<FocusOut>", self.calcular_total)

        # Interstício
        intersticio_padrao = (
            contrato[19] == 1 if contrato and len(contrato) > 19 else False
        )
        # Criar a variável BooleanVar para o checkbox
        intersticio_var = tk.BooleanVar(value=intersticio_padrao)
        self.form_contrato.adicionar_campo(
            "intersticio", "Interstício", tipo="checkbox", padrao=intersticio_padrao
        )
        # Armazenar a variável no dicionário de campos
        self.form_contrato.campos["intersticio"]["var"] = intersticio_var
        # Configurar o widget para usar esta variável
        self.form_contrato.campos["intersticio"]["widget"].configure(
            variable=intersticio_var
        )

        # Valor do interstício
        valor_intersticio_padrao = (
            contrato[20] if contrato and len(contrato) > 20 else ""
        )
        self.form_contrato.adicionar_campo(
            "valor_intersticio",
            "Valor do Interstício",
            tipo="numero",
            padrao=valor_intersticio_padrao,
        )
        # Configurar formatação para valor do interstício
        valor_intersticio_widget = self.form_contrato.campos["valor_intersticio"][
            "widget"
        ]
        valor_intersticio_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(valor_intersticio_widget, e)
        )
        valor_intersticio_widget.bind("<FocusOut>", self.calcular_total)

        # Valor complementar
        valor_complementar_padrao = (
            contrato[21] if contrato and len(contrato) > 21 else ""
        )
        self.form_contrato.adicionar_campo(
            "valor_complementar",
            "Valor Complementar",
            tipo="numero",
            padrao=valor_complementar_padrao,
        )
        # Configurar formatação para valor complementar
        valor_complementar_widget = self.form_contrato.campos["valor_complementar"][
            "widget"
        ]
        valor_complementar_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(valor_complementar_widget, e)
        )
        valor_complementar_widget.bind("<FocusOut>", self.calcular_total)

        # Total do contrato
        total_contrato_padrao = contrato[22] if contrato and len(contrato) > 22 else ""
        self.form_contrato.adicionar_campo(
            "total_contrato",
            "Total do Contrato",
            tipo="numero",
            padrao=total_contrato_padrao,
            required=True,
        )
        # Configurar formatação para total do contrato
        total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
        total_contrato_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(total_contrato_widget, e)
        )

        # Observações
        observacoes_padrao = contrato[23] if contrato and len(contrato) > 23 else ""
        self.form_contrato.adicionar_campo(
            "observacoes", "Observações", tipo="texto_longo", padrao=observacoes_padrao
        )

        # Aba de produtos (quinta aba) - apenas para contratos existentes
        if self.modo_edicao:
            self.tab_produtos = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_produtos, text="Produtos")

            # Frame para a tabela de produtos
            self.frame_tabela_produtos = ttk.Frame(self.tab_produtos)
            self.frame_tabela_produtos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Título e botão para adicionar produto
            frame_cabecalho_produtos = ttk.Frame(self.frame_tabela_produtos)
            frame_cabecalho_produtos.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                frame_cabecalho_produtos,
                text="Produtos do Contrato",
                style="Titulo.TLabel",
            ).pack(side=tk.LEFT)

            # Botão de adicionar produto
            self.btn_adicionar_produto = criar_botao(
                frame_cabecalho_produtos,
                "Adicionar Produto",
                self.adicionar_produto,
                "Primario",
                15,
            )
            self.btn_adicionar_produto.pack(side=tk.RIGHT)

            # Tabela de produtos
            colunas = [
                "id",
                "numero",
                "titulo",
                "data_programada",
                "data_entrega",
                "status",
                "valor",
            ]
            titulos = {
                "id": "ID",
                "numero": "Número",
                "titulo": "Título",
                "data_programada": "Data Programada",
                "data_entrega": "Data Entrega",
                "status": "Status",
                "valor": "Valor (R$)",
            }

            self.tabela_produtos = TabelaBase(
                self.frame_tabela_produtos, colunas, titulos
            )
            self.tabela_produtos.pack(fill=tk.BOTH, expand=True)

            # Frame de botões de ação para produtos
            frame_acoes_produtos = ttk.Frame(self.frame_tabela_produtos)
            frame_acoes_produtos.pack(fill=tk.X, pady=(10, 0))

            criar_botao(
                frame_acoes_produtos,
                "Visualizar",
                self.visualizar_produto,
                "Primario",
                15,
            ).pack(side=tk.LEFT, padx=(0, 5))
            criar_botao(
                frame_acoes_produtos,
                "Editar",
                self.editar_produto,
                "Secundario",
                15,
            ).pack(side=tk.LEFT, padx=(0, 5))
            criar_botao(
                frame_acoes_produtos, "Excluir", self.excluir_produto, "Perigo", 15
            ).pack(side=tk.LEFT)

            # Carregar produtos existentes
            self.carregar_produtos()

        # Aba de aditivos (sexta aba) - apenas para contratos existentes
        if self.modo_edicao:
            self.tab_aditivos = ttk.Frame(self.notebook)
            self.notebook.add(self.tab_aditivos, text="Aditivos")

            # Frame para a tabela de aditivos
            self.frame_tabela_aditivos = ttk.Frame(self.tab_aditivos)
            self.frame_tabela_aditivos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Título e botão para adicionar aditivo
            frame_cabecalho_aditivos = ttk.Frame(self.frame_tabela_aditivos)
            frame_cabecalho_aditivos.pack(fill=tk.X, pady=(0, 10))

            ttk.Label(
                frame_cabecalho_aditivos,
                text="Aditivos do Contrato",
                style="Titulo.TLabel",
            ).pack(side=tk.LEFT)

            # Botão de adicionar aditivo
            self.btn_adicionar_aditivo = criar_botao(
                frame_cabecalho_aditivos,
                "Adicionar Aditivo",
                self.adicionar_aditivo,
                "Primario",
                15,
            )
            self.btn_adicionar_aditivo.pack(side=tk.RIGHT)

            # Tabela de aditivos
            colunas = [
                "id",
                "tipo_aditivo",
                "data_entrada",
                "nova_vigencia_final",
                "nova_remuneracao",
                "valor_total_aditivo",
            ]
            titulos = {
                "id": "ID",
                "tipo_aditivo": "Tipo",
                "data_entrada": "Data de Entrada",
                "nova_vigencia_final": "Nova Vigência Final",
                "nova_remuneracao": "Nova Remuneração (R$)",
                "valor_total_aditivo": "Valor Total (R$)",
            }

            self.tabela_aditivos = TabelaBase(
                self.frame_tabela_aditivos, colunas, titulos
            )
            self.tabela_aditivos.pack(fill=tk.BOTH, expand=True)

            # Frame de botões de ação para aditivos
            frame_acoes_aditivos = ttk.Frame(self.frame_tabela_aditivos)
            frame_acoes_aditivos.pack(fill=tk.X, pady=(10, 0))

            criar_botao(
                frame_acoes_aditivos,
                "Visualizar",
                self.visualizar_aditivo,
                "Primario",
                15,
            ).pack(side=tk.LEFT, padx=(0, 5))
            criar_botao(
                frame_acoes_aditivos, "Excluir", self.excluir_aditivo, "Perigo", 15
            ).pack(side=tk.LEFT)

            # Carregar aditivos existentes
            self.carregar_aditivos()

        # Calcular meses e total inicial
        self.calcular_meses()
        self.calcular_total()

    def carregar_pessoas(self):
        """Carrega a lista de pessoas físicas para o combobox"""
        try:
            pessoas = listar_pessoas()
            nomes_pessoas = [pessoa[1] for pessoa in pessoas]
            self.pessoa_combobox["values"] = nomes_pessoas

            # Mapeamento de nomes para IDs
            self.pessoas_map = {pessoa[1]: pessoa[0] for pessoa in pessoas}

        except Exception as e:
            print(f"Erro ao carregar pessoas: {e}")

    def buscar_pessoa(self):
        """Abre uma janela para buscar pessoa física"""
        # Criar uma janela de diálogo para a busca
        janela = tk.Toplevel(self)
        janela.title("Buscar Pessoa Física")
        janela.transient(self)
        janela.grab_set()

        # Centraliza a janela
        largura = 800
        altura = 500
        pos_x = self.winfo_rootx() + (self.winfo_width() - largura) // 2
        pos_y = self.winfo_rooty() + (self.winfo_height() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        # Frame principal
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        pesquisa_entry.pack(side=tk.LEFT, padx=(0, 5))
        pesquisa_entry.focus_set()

        # Tabela de resultados
        colunas = ["id", "nome_completo", "cpf", "email", "telefone"]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome Completo",
            "cpf": "CPF",
            "email": "E-mail",
            "telefone": "Telefone",
        }

        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True, pady=10)

        # Função para carregar dados na tabela
        def carregar_dados(filtro=None):
            tabela.limpar()

            pessoas = listar_pessoas()

            for pessoa in pessoas:
                # Se tiver filtro, verifica se pessoa contém o texto do filtro
                if filtro:
                    texto_filtro = filtro.lower()
                    texto_pessoa = " ".join(
                        str(campo).lower() for campo in pessoa if campo
                    )
                    if texto_filtro not in texto_pessoa:
                        continue

                valores = {
                    "id": pessoa[0],
                    "nome_completo": pessoa[1],
                    "cpf": pessoa[2] or "",
                    "email": pessoa[3] or "",
                    "telefone": pessoa[4] or "",
                }
                tabela.adicionar_linha(valores, str(pessoa[0]))

        # Carregar dados iniciais
        carregar_dados()

        # Função para pesquisar
        def pesquisar():
            filtro = pesquisa_entry.get().strip()
            carregar_dados(filtro)

        pesquisa_entry.bind("<Return>", lambda e: pesquisar())

        # Botão de pesquisa
        criar_botao(frame_pesquisa, "Buscar", pesquisar, "Primario", 12).pack(
            side=tk.LEFT
        )

        # Função para selecionar a pessoa e fechar a janela
        def selecionar():
            id_selecao = tabela.obter_selecao()
            if id_selecao:
                # Buscar a pessoa selecionada
                pessoa = buscar_pessoa_por_id(id_selecao)
                if pessoa:
                    # Atualizar o combobox e o campo oculto
                    self.pessoa_var.set(pessoa[1])
                    self.id_pessoa_selecionada.set(str(pessoa[0]))
                    self.atualizar_info_pessoa(pessoa)
                    janela.destroy()
            else:
                mostrar_mensagem("Atenção", "Selecione uma pessoa.", tipo="aviso")

        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=10)

        criar_botao(frame_botoes, "Cancelar", janela.destroy, "Secundario", 15).pack(
            side=tk.RIGHT, padx=5
        )
        criar_botao(frame_botoes, "Selecionar", selecionar, "Primario", 15).pack(
            side=tk.RIGHT
        )

    def selecionar_pessoa(self, event=None):
        """Callback quando uma pessoa é selecionada no combobox"""
        nome_pessoa = self.pessoa_var.get()

        if nome_pessoa in self.pessoas_map:
            id_pessoa = self.pessoas_map[nome_pessoa]
            self.id_pessoa_selecionada.set(str(id_pessoa))

            # Buscar dados completos da pessoa
            pessoa = buscar_pessoa_por_id(id_pessoa)
            if pessoa:
                self.atualizar_info_pessoa(pessoa)

    def atualizar_info_pessoa(self, pessoa):
        """Atualiza o label de informações da pessoa"""
        if not pessoa:
            self.info_pessoa_label.config(
                text="Nenhuma pessoa selecionada", foreground="gray"
            )
            return

        cpf = pessoa[2] or "Não informado"
        email = pessoa[3] or "Não informado"

        info_text = f"CPF: {cpf} | E-mail: {email}"
        self.info_pessoa_label.config(text=info_text, foreground="black")

    def calcular_meses(self, event=None):
        """Calcula a quantidade de meses entre as datas de vigência"""
        try:
            vigencia_inicial = self.form_contrato.campos["vigencia_inicial"][
                "widget"
            ].get()
            vigencia_final = self.form_contrato.campos["vigencia_final"]["widget"].get()

            if validar_data(vigencia_inicial) and validar_data(vigencia_final):
                if validar_periodo(vigencia_inicial, vigencia_final):
                    meses = calcular_meses_entre_datas(vigencia_inicial, vigencia_final)

                    # Atualizar o campo de meses
                    meses_widget = self.form_contrato.campos["meses"]["widget"]
                    meses_widget.delete(0, tk.END)
                    meses_widget.insert(0, str(meses))

                    # Recalcular o total
                    self.calcular_total()
                else:
                    mostrar_mensagem(
                        "Erro de Validação",
                        "A data final deve ser posterior à data inicial.",
                        tipo="erro",
                    )
        except Exception as e:
            print(f"Erro ao calcular meses: {e}")

    def calcular_total(self, event=None):
        """Calcula o valor total do contrato"""
        try:
            # Obter valores
            remuneracao = self.form_contrato.campos["remuneracao"]["widget"].get()
            meses = self.form_contrato.campos["meses"]["widget"].get()

            # Para o checkbox, precisamos acessar o valor diretamente
            campo_intersticio = self.form_contrato.campos["intersticio"]
            try:
                # Tenta acessar a variável associada ao checkbox
                if "var" in campo_intersticio:
                    intersticio = campo_intersticio["var"].get()
                else:
                    # Tenta obter o valor diretamente do widget
                    intersticio = campo_intersticio["widget"].get()
            except Exception:
                # Se ocorrer qualquer erro, assume falso
                intersticio = False

            valor_intersticio = self.form_contrato.campos["valor_intersticio"][
                "widget"
            ].get()
            valor_complementar = self.form_contrato.campos["valor_complementar"][
                "widget"
            ].get()

            # Converter valores
            remuneracao_float = converter_valor_brl_para_float(remuneracao)
            meses_int = int(meses) if meses.strip() else 0
            valor_intersticio_float = (
                converter_valor_brl_para_float(valor_intersticio) if intersticio else 0
            )
            valor_complementar_float = converter_valor_brl_para_float(
                valor_complementar
            )

            # Calcular total
            total = (
                (remuneracao_float * meses_int)
                + valor_intersticio_float
                + valor_complementar_float
            )

            # Atualizar o campo de total
            total_widget = self.form_contrato.campos["total_contrato"]["widget"]
            total_widget.delete(0, tk.END)
            total_widget.insert(
                0,
                f"R$ {total:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )

        except Exception as e:
            print(f"Erro ao calcular total: {e}")

    def carregar_aditivos(self):
        """Carrega os aditivos do contrato na tabela"""
        if not hasattr(self, "tabela_aditivos") or not self.id_contrato:
            return

        self.tabela_aditivos.limpar()

        # Obter aditivos do contrato
        aditivos = listar_aditivos_por_contrato(self.id_contrato)

        for aditivo in aditivos:
            # Extrair dados do aditivo
            id_aditivo = aditivo[0]
            tipo_aditivo = aditivo[2]
            data_entrada = aditivo[4]
            nova_vigencia_final = aditivo[14]
            nova_remuneracao = aditivo[17]
            valor_total_aditivo = aditivo[20]

            # Formatar valores monetários
            try:
                if nova_remuneracao:
                    nova_remuneracao_formatada = (
                        f"R$ {float(nova_remuneracao):,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                else:
                    nova_remuneracao_formatada = ""

                if valor_total_aditivo:
                    valor_total_formatado = (
                        f"R$ {float(valor_total_aditivo):,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                else:
                    valor_total_formatado = ""
            except (ValueError, TypeError):
                nova_remuneracao_formatada = ""
                valor_total_formatado = ""

            # Traduzir tipo de aditivo para exibição
            tipo_aditivo_exibicao = {
                "prorrogacao": "Prorrogação",
                "reajuste": "Reajuste",
                "ambos": "Prorrogação e Reajuste",
            }.get(tipo_aditivo, tipo_aditivo)

            # Criar um dicionário com os valores do aditivo
            valores = {
                "id": id_aditivo,
                "tipo_aditivo": tipo_aditivo_exibicao,
                "data_entrada": data_entrada,
                "nova_vigencia_final": nova_vigencia_final,
                "nova_remuneracao": nova_remuneracao_formatada,
                "valor_total_aditivo": valor_total_formatado,
            }

            self.tabela_aditivos.adicionar_linha(valores, str(id_aditivo))

    def adicionar_aditivo(self):
        """Abre o formulário para adicionar um novo aditivo"""
        if not self.id_contrato:
            mostrar_mensagem(
                "Atenção",
                "É necessário salvar o contrato antes de adicionar aditivos.",
                tipo="aviso",
            )
            return

        # Verificar modalidade do contrato
        modalidade = self.form_contrato.campos["modalidade"]["widget"].get()

        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Aditivo")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()

        # Formulário para o aditivo
        form_aditivo = FormularioBase(dialog, "Novo Aditivo de Contrato")
        form_aditivo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tipo de aditivo
        tipos_aditivo = ["prorrogacao", "reajuste", "ambos"]
        form_aditivo.adicionar_campo(
            "tipo_aditivo",
            "Tipo de Aditivo",
            tipo="opcoes",
            opcoes=tipos_aditivo,
            padrao=tipos_aditivo[0],
            required=True,
        )

        # Campo tipo_aditivo
        tipo_aditivo_widget = form_aditivo.campos["tipo_aditivo"]["widget"]

        # Ofício
        form_aditivo.adicionar_campo("oficio", "Ofício", padrao="", required=True)

        # Data de entrada
        form_aditivo.adicionar_campo(
            "data_entrada", "Data de Entrada", tipo="data", padrao="", required=True
        )
        # Formatação para data de entrada
        data_entrada_widget = form_aditivo.campos["data_entrada"]["widget"]
        data_entrada_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_entrada_widget, e)
        )

        # Data de protocolo
        form_aditivo.adicionar_campo(
            "data_protocolo", "Data de Protocolo", tipo="data", padrao=""
        )
        # Formatação para data de protocolo
        data_protocolo_widget = form_aditivo.campos["data_protocolo"]["widget"]
        data_protocolo_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_protocolo_widget, e)
        )

        # Frame para notebook com abas específicas por tipo de aditivo
        frame_notebook = ttk.Frame(form_aditivo)
        frame_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Notebook para separar os campos por tipo de aditivo
        notebook = ttk.Notebook(frame_notebook)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de prorrogação
        tab_prorrogacao = ttk.Frame(notebook)
        notebook.add(tab_prorrogacao, text="Prorrogação")

        # Formulário para prorrogação
        form_prorrogacao = FormularioBase(tab_prorrogacao, "")
        form_prorrogacao.pack(fill=tk.BOTH, expand=True)

        # Nova vigência final
        form_prorrogacao.adicionar_campo(
            "nova_vigencia_final",
            "Nova Vigência Final",
            tipo="data",
            padrao="",
            required=True,
        )
        # Formatação para nova vigência final
        nova_vigencia_widget = form_prorrogacao.campos["nova_vigencia_final"]["widget"]
        nova_vigencia_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(nova_vigencia_widget, e)
        )

        # Meses adicionais
        form_prorrogacao.adicionar_campo(
            "meses", "Meses Adicionais", tipo="numero", padrao="", required=True
        )

        # Aba de reajuste
        tab_reajuste = ttk.Frame(notebook)
        notebook.add(tab_reajuste, text="Reajuste")

        # Formulário para reajuste
        form_reajuste = FormularioBase(tab_reajuste, "")
        form_reajuste.pack(fill=tk.BOTH, expand=True)

        # Remuneração atual
        remuneracao_atual = self.form_contrato.campos["remuneracao"]["widget"].get()
        form_reajuste.adicionar_campo(
            "remuneracao_atual",
            "Remuneração Atual",
            tipo="numero",
            padrao=remuneracao_atual,
            required=False,
        )
        # Configurar campo como somente leitura
        remuneracao_atual_widget = form_reajuste.campos["remuneracao_atual"]["widget"]
        remuneracao_atual_widget.configure(state="readonly")

        # Nova remuneração
        form_reajuste.adicionar_campo(
            "nova_remuneracao",
            "Nova Remuneração",
            tipo="numero",
            padrao="",
            required=True,
        )
        # Formatação para nova remuneração
        nova_remuneracao_widget = form_reajuste.campos["nova_remuneracao"]["widget"]
        nova_remuneracao_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(nova_remuneracao_widget, e)
        )

        # Função para calcular a diferença de remuneração
        def calcular_diferenca_remuneracao():
            try:
                remuneracao_atual_valor = converter_valor_brl_para_float(
                    remuneracao_atual
                )
                nova_remuneracao_valor = converter_valor_brl_para_float(
                    nova_remuneracao_widget.get()
                )

                diferenca = nova_remuneracao_valor - remuneracao_atual_valor

                diferenca_widget.configure(state="normal")
                diferenca_widget.delete(0, tk.END)
                diferenca_widget.insert(
                    0,
                    f"R$ {diferenca:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )
                diferenca_widget.configure(state="readonly")
            except Exception as e:
                print(f"Erro ao calcular diferença de remuneração: {e}")

        nova_remuneracao_widget.bind(
            "<FocusOut>", lambda e: calcular_diferenca_remuneracao()
        )

        # Diferença de remuneração
        form_reajuste.adicionar_campo(
            "diferenca_remuneracao",
            "Diferença de Remuneração",
            tipo="numero",
            padrao="",
            required=False,
        )
        # Configurar campo como somente leitura
        diferenca_widget = form_reajuste.campos["diferenca_remuneracao"]["widget"]
        diferenca_widget.configure(state="readonly")

        # Campos comuns para todos os tipos de aditivo
        frame_campos_comuns = ttk.Frame(form_aditivo)
        frame_campos_comuns.pack(fill=tk.X, pady=10)

        # Valor complementar
        form_aditivo.adicionar_campo(
            "valor_complementar", "Valor Complementar", tipo="numero", padrao=""
        )
        # Formatação para valor complementar
        valor_complementar_widget = form_aditivo.campos["valor_complementar"]["widget"]
        valor_complementar_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(valor_complementar_widget, e)
        )

        # Responsável
        form_aditivo.adicionar_campo(
            "responsavel", "Responsável", padrao="", required=True
        )

        # Função para alternar abas com base no tipo de aditivo
        def alternar_abas(event=None):
            tipo = tipo_aditivo_widget.get()

            if tipo == "prorrogacao":
                notebook.select(0)  # Seleciona a aba de prorrogação
            elif tipo == "reajuste":
                notebook.select(1)  # Seleciona a aba de reajuste
            elif tipo == "ambos":
                # Ambos tipos, deixa na aba atual
                pass

        # Vincular evento de seleção do tipo de aditivo
        tipo_aditivo_widget.bind("<<ComboboxSelected>>", alternar_abas)

        # Frame para botões
        frame_botoes = ttk.Frame(dialog)
        frame_botoes.pack(fill=tk.X, padx=20, pady=10)

        # Função para salvar o aditivo
        def salvar_aditivo():
            # Validar o formulário principal
            valido, mensagem = form_aditivo.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return

            # Obter tipo de aditivo
            tipo_aditivo = tipo_aditivo_widget.get()

            # Validar formulários específicos por tipo
            if tipo_aditivo in ["prorrogacao", "ambos"]:
                valido_prorrogacao, mensagem_prorrogacao = form_prorrogacao.validar()
                if not valido_prorrogacao:
                    mostrar_mensagem(
                        "Erro de Validação", mensagem_prorrogacao, tipo="erro"
                    )
                    return

            if tipo_aditivo in ["reajuste", "ambos"]:
                valido_reajuste, mensagem_reajuste = form_reajuste.validar()
                if not valido_reajuste:
                    mostrar_mensagem(
                        "Erro de Validação", mensagem_reajuste, tipo="erro"
                    )
                    return

            try:
                # Obter valores do formulário principal
                valores = form_aditivo.obter_valores()

                # Inicializar valores específicos por tipo
                nova_vigencia_final = None
                meses = None
                nova_remuneracao = None
                diferenca_remuneracao = None

                # Obter valores específicos por tipo
                if tipo_aditivo in ["prorrogacao", "ambos"]:
                    valores_prorrogacao = form_prorrogacao.obter_valores()
                    nova_vigencia_final = valores_prorrogacao["nova_vigencia_final"]
                    meses = int(valores_prorrogacao["meses"])

                if tipo_aditivo in ["reajuste", "ambos"]:
                    valores_reajuste = form_reajuste.obter_valores()
                    nova_remuneracao = converter_valor_brl_para_float(
                        valores_reajuste["nova_remuneracao"]
                    )
                    diferenca_remuneracao = converter_valor_brl_para_float(
                        valores_reajuste["diferenca_remuneracao"]
                    )

                # Converter valores monetários
                valor_complementar = converter_valor_brl_para_float(
                    valores["valor_complementar"]
                )

                # Calcular valor total do aditivo
                valor_total_aditivo = 0

                if tipo_aditivo == "prorrogacao":
                    # Para prorrogação, usar a remuneração atual * meses
                    remuneracao_atual_valor = converter_valor_brl_para_float(
                        remuneracao_atual
                    )
                    valor_total_aditivo = (
                        remuneracao_atual_valor * meses
                    ) + valor_complementar
                elif tipo_aditivo == "reajuste":
                    # Para reajuste, pegar a diferença de remuneração * meses do contrato
                    meses_contrato = int(
                        self.form_contrato.campos["meses"]["widget"].get()
                    )
                    valor_total_aditivo = (
                        diferenca_remuneracao * meses_contrato
                    ) + valor_complementar
                elif tipo_aditivo == "ambos":
                    # Para ambos, somar a nova remuneração * novos meses + diferença de remuneração * meses antigos
                    meses_contrato = int(
                        self.form_contrato.campos["meses"]["widget"].get()
                    )
                    valor_total_aditivo = (
                        (nova_remuneracao * meses)
                        + (diferenca_remuneracao * meses_contrato)
                        + valor_complementar
                    )

                # Criar o aditivo
                adicionar_aditivo(
                    id_contrato=self.id_contrato,
                    tipo_aditivo=tipo_aditivo,
                    oficio=valores["oficio"],
                    data_entrada=valores["data_entrada"],
                    data_protocolo=valores["data_protocolo"],
                    vigencia_final=nova_vigencia_final,
                    meses=meses,
                    valor_aditivo=0,  # Será calculado pela soma dos outros valores
                    nova_remuneracao=nova_remuneracao,
                    diferenca_remuneracao=diferenca_remuneracao,
                    valor_complementar=valor_complementar,
                    valor_total_aditivo=valor_total_aditivo,
                    responsavel=valores["responsavel"],
                )

                mostrar_mensagem(
                    "Sucesso", "Aditivo adicionado com sucesso!", tipo="sucesso"
                )

                # Atualizar contrato se for edição
                if self.modo_edicao:
                    # Atualizar campos do contrato conforme o aditivo
                    if tipo_aditivo in ["prorrogacao", "ambos"]:
                        # Atualizar vigência final e meses
                        self.form_contrato.campos["vigencia_final"]["widget"].delete(
                            0, tk.END
                        )
                        self.form_contrato.campos["vigencia_final"]["widget"].insert(
                            0, nova_vigencia_final
                        )

                        # Atualizar meses (somar os novos meses)
                        meses_contrato = int(
                            self.form_contrato.campos["meses"]["widget"].get()
                        )
                        self.form_contrato.campos["meses"]["widget"].delete(0, tk.END)
                        self.form_contrato.campos["meses"]["widget"].insert(
                            0, str(meses_contrato + meses)
                        )

                    if tipo_aditivo in ["reajuste", "ambos"]:
                        # Atualizar remuneração
                        self.form_contrato.campos["remuneracao"]["widget"].delete(
                            0, tk.END
                        )
                        self.form_contrato.campos["remuneracao"]["widget"].insert(
                            0,
                            f"R$ {nova_remuneracao:,.2f}".replace(",", "X")
                            .replace(".", ",")
                            .replace("X", "."),
                        )

                    # Atualizar total do contrato
                    total_contrato = float(
                        converter_valor_brl_para_float(
                            self.form_contrato.campos["total_contrato"]["widget"].get()
                        )
                    )
                    novo_total = total_contrato + valor_total_aditivo

                    self.form_contrato.campos["total_contrato"]["widget"].delete(
                        0, tk.END
                    )
                    self.form_contrato.campos["total_contrato"]["widget"].insert(
                        0,
                        f"R$ {novo_total:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", "."),
                    )

                # Recarregar aditivos
                self.carregar_aditivos()

                # Fechar o diálogo
                dialog.destroy()

            except Exception as e:
                mostrar_mensagem(
                    "Erro", f"Erro ao salvar aditivo: {str(e)}", tipo="erro"
                )

        # Botões de ação
        criar_botao(frame_botoes, "Cancelar", dialog.destroy, "Secundario", 15).pack(
            side=tk.RIGHT, padx=5
        )
        criar_botao(frame_botoes, "Salvar", salvar_aditivo, "Primario", 15).pack(
            side=tk.RIGHT
        )

    def visualizar_aditivo(self):
        """Visualiza os detalhes de um aditivo (somente leitura)"""
        if not hasattr(self, "tabela_aditivos"):
            return

        id_selecao = self.tabela_aditivos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um aditivo para visualizar.", tipo="aviso"
            )
            return

        # TODO: Implementar visualização de aditivo
        mostrar_mensagem(
            "Visualizar Aditivo", f"Visualizando aditivo ID: {id_selecao}", tipo="info"
        )

    def carregar_produtos(self):
        """Carrega os produtos do contrato na tabela"""
        if not hasattr(self, "tabela_produtos") or not self.id_contrato:
            return

        self.tabela_produtos.limpar()

        # Obter produtos do contrato
        produtos = listar_produtos_por_contrato(self.id_contrato)

        for produto in produtos:
            # Extrair dados do produto
            id_produto = produto[0]
            numero = produto[2]
            titulo = produto[7]
            data_programada = produto[3]
            data_entrega = produto[5]
            status = produto[6]
            valor = produto[8]

            # Formatar datas
            data_programada_formatada = data_programada
            if data_programada:
                try:
                    data_programada_formatada = datetime.strptime(
                        data_programada, "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                except ValueError:
                    pass

            data_entrega_formatada = data_entrega or "-"
            if data_entrega:
                try:
                    data_entrega_formatada = datetime.strptime(
                        data_entrega, "%Y-%m-%d"
                    ).strftime("%d/%m/%Y")
                except ValueError:
                    pass

            # Formatar valor monetário
            try:
                if valor:
                    valor_formatado = (
                        f"R$ {float(valor):,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                else:
                    valor_formatado = "R$ 0,00"
            except (ValueError, TypeError):
                valor_formatado = "R$ 0,00"

            # Traduzir status para exibição
            status_map = {
                "programado": "Programado",
                "em_execucao": "Em Execução",
                "entregue": "Entregue",
                "cancelado": "Cancelado",
            }
            status_exibicao = status_map.get(status, status)

            # Criar um dicionário com os valores do produto
            valores = {
                "id": id_produto,
                "numero": numero,
                "titulo": titulo,
                "data_programada": data_programada_formatada,
                "data_entrega": data_entrega_formatada,
                "status": status_exibicao,
                "valor": valor_formatado,
            }

            self.tabela_produtos.adicionar_linha(valores, str(id_produto))

    def adicionar_produto(self):
        """Abre o formulário para adicionar um novo produto"""
        if not self.id_contrato:
            mostrar_mensagem(
                "Atenção",
                "É necessário salvar o contrato antes de adicionar produtos.",
                tipo="aviso",
            )
            return

        # Verificar modalidade do contrato
        modalidade = self.form_contrato.campos["modalidade"]["widget"].get()
        if modalidade == "CLT":
            mostrar_mensagem(
                "Atenção",
                "Contratos CLT não podem ter produtos associados.",
                tipo="aviso",
            )
            return

        # Importar a view de produto
        from views.produto_pf_view import ProdutoPFForm

        # Criar uma janela de diálogo para o formulário de produto
        dialog = tk.Toplevel(self)
        dialog.title("Adicionar Produto")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()

        # Função de callback para quando o produto for salvo
        def produto_salvo():
            dialog.destroy()
            self.carregar_produtos()

        # Função de callback para quando o formulário for cancelado
        def produto_cancelado():
            dialog.destroy()

        # Criar o formulário de produto
        form_produto = ProdutoPFForm(
            dialog,
            callback_salvar=produto_salvo,
            callback_cancelar=produto_cancelado,
            id_contrato=self.id_contrato,
        )
        form_produto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def visualizar_produto(self):
        """Visualiza os detalhes de um produto (somente leitura)"""
        if not hasattr(self, "tabela_produtos"):
            return

        id_selecao = self.tabela_produtos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um produto para visualizar.", tipo="aviso"
            )
            return

        # Buscar o produto selecionado
        produto = buscar_produto_por_id(id_selecao)
        if not produto:
            mostrar_mensagem("Erro", "Produto não encontrado.", tipo="erro")
            return

        # Importar a view de produto
        from views.produto_pf_view import ProdutoPFForm

        # Criar uma janela modal para visualização
        janela = tk.Toplevel(self)
        janela.title("Visualizar Produto")
        janela.transient(self)
        janela.grab_set()

        # Centraliza a janela
        largura = 650
        altura = 600
        pos_x = self.winfo_rootx() + (self.winfo_width() - largura) // 2
        pos_y = self.winfo_rooty() + (self.winfo_height() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        # Cria o formulário de visualização
        form = ProdutoPFForm(
            janela,
            callback_salvar=janela.destroy,
            callback_cancelar=janela.destroy,
            produto=produto,
        )
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Desabilita os campos para visualização
        for nome, info in form.campos.items():
            info["widget"].configure(state="disabled")

        # Desabilitar combobox de contrato
        form.contrato_combobox.configure(state="disabled")

        # Altera os botões
        for widget in form.winfo_children():
            if (
                isinstance(widget, ttk.Frame) and widget == form.winfo_children()[-1]
            ):  # Último frame (botões)
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Frame):  # Frame do botão
                        for btn in child.winfo_children():
                            if isinstance(btn, tk.Button) and btn["text"] == "Salvar":
                                btn.destroy()  # Remove o botão Salvar
                            elif (
                                isinstance(btn, tk.Button) and btn["text"] == "Cancelar"
                            ):
                                btn.configure(
                                    text="Fechar"
                                )  # Altera o texto do botão Cancelar

    def editar_produto(self):
        """Edita um produto existente"""
        if not hasattr(self, "tabela_produtos"):
            return

        id_selecao = self.tabela_produtos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um produto para editar.", tipo="aviso"
            )
            return

        # Buscar o produto selecionado
        produto = buscar_produto_por_id(id_selecao)
        if not produto:
            mostrar_mensagem("Erro", "Produto não encontrado.", tipo="erro")
            return

        # Importar a view de produto
        from views.produto_pf_view import ProdutoPFForm

        # Criar uma janela de diálogo para o formulário de produto
        dialog = tk.Toplevel(self)
        dialog.title("Editar Produto")
        dialog.geometry("800x600")
        dialog.transient(self)
        dialog.grab_set()

        # Função de callback para quando o produto for salvo
        def produto_salvo():
            dialog.destroy()
            self.carregar_produtos()

        # Função de callback para quando o formulário for cancelado
        def produto_cancelado():
            dialog.destroy()

        # Criar o formulário de produto
        form_produto = ProdutoPFForm(
            dialog,
            callback_salvar=produto_salvo,
            callback_cancelar=produto_cancelado,
            produto=produto,
        )
        form_produto.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def excluir_produto(self):
        """Exclui o produto selecionado"""
        if not hasattr(self, "tabela_produtos"):
            return

        id_selecao = self.tabela_produtos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um produto para excluir.", tipo="aviso"
            )
            return

        if mostrar_mensagem(
            "Confirmação", "Deseja realmente excluir este produto?", tipo="pergunta"
        ):
            try:
                excluir_produto(id_selecao)
                mostrar_mensagem(
                    "Sucesso", "Produto excluído com sucesso!", tipo="sucesso"
                )
                self.carregar_produtos()
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao excluir produto: {e}", tipo="erro")

    def excluir_aditivo(self):
        """Exclui o aditivo selecionado"""
        if not hasattr(self, "tabela_aditivos"):
            return

        id_selecao = self.tabela_aditivos.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um aditivo para excluir.", tipo="aviso"
            )
            return

        if mostrar_mensagem(
            "Confirmação", "Deseja realmente excluir este aditivo?", tipo="pergunta"
        ):
            try:
                excluir_aditivo(id_selecao)
                mostrar_mensagem(
                    "Sucesso", "Aditivo excluído com sucesso!", tipo="sucesso"
                )
                self.carregar_aditivos()

                # Recalcular total do contrato
                atualizar_total_contrato(self.id_contrato)

                # Recarregar os dados do contrato
                contrato = buscar_contrato_por_id(self.id_contrato)
                if contrato:
                    # Atualizar os campos do formulário
                    self.form_contrato.campos["total_contrato"]["widget"].delete(
                        0, tk.END
                    )
                    self.form_contrato.campos["total_contrato"]["widget"].insert(
                        0,
                        f"R$ {float(contrato[22]):,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", "."),
                    )

                    # Atualizar outros campos relevantes
                    self.form_contrato.campos["vigencia_final"]["widget"].delete(
                        0, tk.END
                    )
                    self.form_contrato.campos["vigencia_final"]["widget"].insert(
                        0, contrato[15]
                    )

                    self.form_contrato.campos["meses"]["widget"].delete(0, tk.END)
                    self.form_contrato.campos["meses"]["widget"].insert(
                        0, str(contrato[16])
                    )

                    self.form_contrato.campos["remuneracao"]["widget"].delete(0, tk.END)
                    self.form_contrato.campos["remuneracao"]["widget"].insert(
                        0,
                        f"R$ {float(contrato[18]):,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", "."),
                    )

            except ValueError as e:
                mostrar_mensagem("Erro", str(e), tipo="erro")

    def salvar(self):
        """Salva os dados do formulário"""
        # Validar todos os formulários
        formularios = [
            self.form_pessoa,
            self.form_demanda,
            self.form_custeio,
            self.form_contrato,
        ]

        for form in formularios:
            valido, mensagem = form.validar()
            if not valido:
                mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
                return

        try:
            # Verificar se uma pessoa foi selecionada
            id_pessoa = self.id_pessoa_selecionada.get()
            if not id_pessoa:
                mostrar_mensagem(
                    "Erro de Validação", "Selecione uma pessoa física.", tipo="erro"
                )
                return

            if self.modo_edicao:
                # Obter valores
                valores_contrato = self.form_contrato.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()

                # Atualizar a demanda se os campos estiverem presentes
                valores_demanda = self.form_demanda.obter_valores()
                codigo_demanda = int(valores_demanda["codigo_demanda"])

                # Editar demanda
                from controllers.demanda_controller import editar_demanda

                editar_demanda(
                    codigo_demanda,
                    valores_demanda["data_entrada"],
                    valores_demanda["solicitante"],
                    valores_demanda["data_protocolo"],
                    valores_demanda["oficio"],
                    valores_demanda["nup_sei"],
                    valores_demanda["status"],
                )

                # Converter valores
                # Obter o valor do checkbox com tratamento de erro
                try:
                    campo_intersticio = self.form_contrato.campos["intersticio"]
                    if "var" in campo_intersticio:
                        intersticio = 1 if campo_intersticio["var"].get() else 0
                    else:
                        # Tenta obter o valor diretamente do widget
                        intersticio = 1 if campo_intersticio["widget"].get() else 0
                except Exception:
                    # Se ocorrer qualquer erro, assume 0
                    intersticio = 0

                remuneracao = converter_valor_brl_para_float(
                    valores_contrato["remuneracao"]
                )
                valor_intersticio = converter_valor_brl_para_float(
                    valores_contrato["valor_intersticio"]
                )
                valor_complementar = converter_valor_brl_para_float(
                    valores_contrato["valor_complementar"]
                )
                total_contrato = converter_valor_brl_para_float(
                    valores_contrato["total_contrato"]
                )

                # Editar contrato
                editar_contrato(
                    self.id_contrato,
                    codigo_demanda,
                    int(id_pessoa),
                    valores_custeio["instituicao"],
                    valores_custeio["instrumento"],
                    valores_custeio["subprojeto"],
                    valores_custeio["ta"],
                    valores_custeio["pta"],
                    valores_custeio["acao"],
                    valores_custeio["resultado"],
                    valores_custeio["meta"],
                    valores_contrato["modalidade"],
                    valores_contrato["natureza_demanda"],
                    valores_contrato["numero_contrato"],
                    valores_contrato["vigencia_inicial"],
                    valores_contrato["vigencia_final"],
                    int(valores_contrato["meses"]),
                    valores_contrato["status_contrato"],
                    remuneracao,
                    intersticio,
                    valor_intersticio,
                    valor_complementar,
                    total_contrato,
                    valores_contrato["observacoes"],
                )

                mostrar_mensagem(
                    "Sucesso", "Contrato atualizado com sucesso!", tipo="sucesso"
                )
            else:
                # Cadastrar nova demanda
                valores_demanda = self.form_demanda.obter_valores()

                # Criar a demanda
                from controllers.demanda_controller import adicionar_demanda

                adicionar_demanda(
                    valores_demanda["data_entrada"],
                    valores_demanda["solicitante"],
                    valores_demanda["data_protocolo"],
                    valores_demanda["oficio"],
                    valores_demanda["nup_sei"],
                    valores_demanda["status"],
                )

                # Obter o código da nova demanda (última demanda inserida)
                demandas = listar_demandas()
                codigo_demanda = demandas[-1][0] if demandas else 1

                # Obter valores do contrato
                valores_contrato = self.form_contrato.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()

                # Converter valores
                # Obter o valor do checkbox com tratamento de erro
                try:
                    campo_intersticio = self.form_contrato.campos["intersticio"]
                    if "var" in campo_intersticio:
                        intersticio = 1 if campo_intersticio["var"].get() else 0
                    else:
                        # Tenta obter o valor diretamente do widget
                        intersticio = 1 if campo_intersticio["widget"].get() else 0
                except Exception:
                    # Se ocorrer qualquer erro, assume 0
                    intersticio = 0

                remuneracao = converter_valor_brl_para_float(
                    valores_contrato["remuneracao"]
                )
                valor_intersticio = converter_valor_brl_para_float(
                    valores_contrato["valor_intersticio"]
                )
                valor_complementar = converter_valor_brl_para_float(
                    valores_contrato["valor_complementar"]
                )
                total_contrato = converter_valor_brl_para_float(
                    valores_contrato["total_contrato"]
                )

                # Adicionar contrato
                adicionar_contrato(
                    codigo_demanda,
                    int(id_pessoa),
                    valores_custeio["instituicao"],
                    valores_custeio["instrumento"],
                    valores_custeio["subprojeto"],
                    valores_custeio["ta"],
                    valores_custeio["pta"],
                    valores_custeio["acao"],
                    valores_custeio["resultado"],
                    valores_custeio["meta"],
                    valores_contrato["modalidade"],
                    valores_contrato["natureza_demanda"],
                    valores_contrato["numero_contrato"],
                    valores_contrato["vigencia_inicial"],
                    valores_contrato["vigencia_final"],
                    int(valores_contrato["meses"]),
                    valores_contrato["status_contrato"],
                    remuneracao,
                    intersticio,
                    valor_intersticio,
                    valor_complementar,
                    total_contrato,
                    valores_contrato["observacoes"],
                )

                mostrar_mensagem(
                    "Sucesso",
                    "Demanda e Contrato cadastrados com sucesso!",
                    tipo="sucesso",
                )

            self.callback_salvar()
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao salvar: {str(e)}", tipo="erro")

    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


class ContratoPFView:
    """Tela principal de listagem e gestão de contratos de pessoa física"""

    def __init__(self, master):
        self.master = master

        # Verifica se o master é uma janela principal para definir o título
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Contratos de Pessoa Física")

        # Configura estilos
        Estilos.configurar()

        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            frame_cabecalho, text="Gestão de Contratos", style="Titulo.TLabel"
        ).pack(side=tk.LEFT)
        criar_botao(
            frame_cabecalho, "Novo Contrato", self.adicionar, "Primario", 15
        ).pack(side=tk.RIGHT)

        # Frame de pesquisa
        frame_pesquisa = ttk.Frame(self.frame)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        self.pesquisa_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry.bind("<Return>", lambda e: self.pesquisar())

        criar_botao(frame_pesquisa, "Buscar", self.pesquisar, "Primario", 12).pack(
            side=tk.LEFT
        )
        criar_botao(
            frame_pesquisa, "Limpar", self.limpar_pesquisa, "Primario", 12
        ).pack(side=tk.LEFT, padx=(5, 0))

        # Frame de filtros
        frame_filtros = ttk.Frame(self.frame)
        frame_filtros.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_filtros, text="Filtrar por:").pack(side=tk.LEFT, padx=(0, 5))

        # Filtro por modalidade
        ttk.Label(frame_filtros, text="Modalidade:").pack(side=tk.LEFT, padx=(10, 5))
        self.filtro_modalidade = ttk.Combobox(
            frame_filtros, values=["Todos", "BOLSA", "PRODUTO", "RPA", "CLT"], width=15
        )
        self.filtro_modalidade.current(0)
        self.filtro_modalidade.pack(side=tk.LEFT, padx=(0, 10))

        # Filtro por status
        ttk.Label(frame_filtros, text="Status:").pack(side=tk.LEFT, padx=(10, 5))
        self.filtro_status = ttk.Combobox(
            frame_filtros,
            values=[
                "Todos",
                "pendente_assinatura",
                "cancelado",
                "concluido",
                "em_tramitacao",
                "aguardando_autorizacao",
                "nao_autorizado",
                "rescindido",
                "vigente",
            ],
            width=20,
        )
        self.filtro_status.current(0)
        self.filtro_status.pack(side=tk.LEFT, padx=(0, 10))

        # Botão para aplicar filtros
        criar_botao(
            frame_filtros, "Aplicar Filtros", self.aplicar_filtros, "Primario", 12
        ).pack(side=tk.LEFT)

        # Tabela de contratos
        colunas = [
            "id",
            "nome_completo",
            "modalidade",
            "numero_contrato",
            "vigencia_inicial",
            "vigencia_final",
            "status_contrato",
            "total_contrato",
        ]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome",
            "modalidade": "Modalidade",
            "numero_contrato": "Número do Contrato",
            "vigencia_inicial": "Início Vigência",
            "vigencia_final": "Fim Vigência",
            "status_contrato": "Status",
            "total_contrato": "Valor Total (R$)",
        }

        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)

        # Frame de botões de ação
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))

        criar_botao(frame_acoes, "Visualizar", self.visualizar, "Primario", 15).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        criar_botao(frame_acoes, "Editar", self.editar, "Secundario", 15).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        criar_botao(frame_acoes, "Excluir", self.excluir, "Perigo", 15).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        criar_botao(
            frame_acoes, "Ver Produtos", self.ver_produtos, "Primario", 15
        ).pack(side=tk.LEFT)

        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)

        # Carrega os dados
        self.carregar_dados()

    def carregar_dados(self, filtro=None, filtro_modalidade=None, filtro_status=None):
        """Carrega os dados dos contratos na tabela"""
        self.tabela.limpar()

        contratos = listar_contratos()

        for contrato in contratos:
            # Aplicar filtros
            if filtro:
                texto_filtro = filtro.lower()
                texto_contrato = " ".join(
                    str(campo).lower() for campo in contrato if campo
                )
                if texto_filtro not in texto_contrato:
                    continue

            if filtro_modalidade and filtro_modalidade != "Todos":
                if contrato[11] != filtro_modalidade:
                    continue

            if filtro_status and filtro_status != "Todos":
                if contrato[17] != filtro_status:
                    continue

            # Status para exibição
            status_map = {
                "pendente_assinatura": "Pendente Assinatura",
                "cancelado": "Cancelado",
                "concluido": "Concluído",
                "em_tramitacao": "Em Tramitação",
                "aguardando_autorizacao": "Aguardando Autorização",
                "nao_autorizado": "Não Autorizado",
                "rescindido": "Rescindido",
                "vigente": "Vigente",
            }
            status_exibicao = status_map.get(contrato[17], contrato[17])

            # Formatação de valor monetário
            try:
                valor_total = float(contrato[22]) if contrato[22] else 0.0
                valor_formatado = (
                    f"R$ {valor_total:,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )
            except (ValueError, TypeError):
                valor_formatado = "R$ 0,00"

            # Nome da pessoa física
            nome_pessoa = contrato[-1] if len(contrato) > 23 else "N/A"

            valores = {
                "id": contrato[0],
                "nome_completo": nome_pessoa,
                "modalidade": contrato[11],
                "numero_contrato": contrato[13],
                "vigencia_inicial": contrato[14],
                "vigencia_final": contrato[15],
                "status_contrato": status_exibicao,
                "total_contrato": valor_formatado,
            }
            self.tabela.adicionar_linha(valores, str(contrato[0]))

    def pesquisar(self):
        """Filtra os contratos conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        modalidade = (
            self.filtro_modalidade.get()
            if self.filtro_modalidade.get() != "Todos"
            else None
        )
        status = (
            self.filtro_status.get() if self.filtro_status.get() != "Todos" else None
        )

        self.carregar_dados(texto, modalidade, status)

    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.filtro_modalidade.current(0)
        self.filtro_status.current(0)
        self.carregar_dados()

    def aplicar_filtros(self):
        """Aplica os filtros selecionados"""
        texto = self.pesquisa_entry.get().strip()
        modalidade = (
            self.filtro_modalidade.get()
            if self.filtro_modalidade.get() != "Todos"
            else None
        )
        status = (
            self.filtro_status.get() if self.filtro_status.get() != "Todos" else None
        )

        self.carregar_dados(texto, modalidade, status)

    def adicionar(self):
        """Abre o formulário para adicionar um novo contrato"""
        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário
        self.formulario = ContratoPFForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def visualizar(self):
        """Abre o formulário para visualizar o contrato selecionado (somente leitura)"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um contrato para visualizar.", tipo="aviso"
            )
            return

        # Busca o contrato selecionado
        contrato = buscar_contrato_por_id(id_selecao)
        if not contrato:
            mostrar_mensagem("Erro", "Contrato não encontrado.", tipo="erro")
            return

        # Cria uma janela modal para visualização
        janela = tk.Toplevel(self.master)
        janela.title("Visualizar Contrato")
        janela.transient(self.master)
        janela.grab_set()

        # Maximiza a janela
        janela.state("zoomed")

        # Cria o formulário de visualização
        form = ContratoPFForm(
            janela,
            callback_salvar=janela.destroy,
            callback_cancelar=janela.destroy,
            contrato=contrato,
        )
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Desabilita os campos para visualização
        def desabilitar_campos():
            for nome, info in form.form_pessoa.campos.items():
                info["widget"].configure(state="disabled")

            for nome, info in form.form_demanda.campos.items():
                info["widget"].configure(state="disabled")

            for nome, info in form.form_custeio.campos.items():
                info["widget"].configure(state="disabled")

            for nome, info in form.form_contrato.campos.items():
                # Alguns campos podem ser especiais, como o checkbox
                if info["tipo"] == "checkbox":
                    continue
                elif info["tipo"] == "texto_longo":
                    info["widget"].configure(state="disabled")
                else:
                    info["widget"].configure(state="disabled")

            # Desabilitar o combobox de pessoa física
            form.pessoa_combobox.configure(state="disabled")

            # Alterar os botões
            for widget in form.frame_botoes.winfo_children():
                if isinstance(widget, ttk.Frame):  # Frame do botão
                    for btn in widget.winfo_children():
                        if isinstance(btn, tk.Button) and btn["text"] == "Salvar":
                            btn.destroy()  # Remove o botão Salvar
                        elif isinstance(btn, tk.Button) and btn["text"] == "Cancelar":
                            btn.configure(
                                text="Fechar"
                            )  # Altera o texto do botão Cancelar

        # Executa a função após um pequeno delay
        self.master.after(100, desabilitar_campos)

    def editar(self):
        """Abre o formulário para editar o contrato selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um contrato para editar.", tipo="aviso"
            )
            return

        # Busca o contrato selecionado
        contrato = buscar_contrato_por_id(id_selecao)
        if not contrato:
            mostrar_mensagem("Erro", "Contrato não encontrado.", tipo="erro")
            return

        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário de edição
        self.formulario = ContratoPFForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
            contrato=contrato,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def excluir(self):
        """Exclui o contrato selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um contrato para excluir.", tipo="aviso"
            )
            return

        if mostrar_mensagem(
            "Confirmação", "Deseja realmente excluir este contrato?", tipo="pergunta"
        ):
            try:
                excluir_contrato(id_selecao)
                mostrar_mensagem(
                    "Sucesso", "Contrato excluído com sucesso!", tipo="sucesso"
                )
                self.carregar_dados()
            except ValueError as e:
                mostrar_mensagem("Erro", str(e), tipo="erro")

    def ver_produtos(self):
        """Abre uma janela para visualizar os produtos do contrato selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um contrato para ver seus produtos.", tipo="aviso"
            )
            return

        # Verificar modalidade do contrato
        contrato = buscar_contrato_por_id(id_selecao)
        if not contrato:
            mostrar_mensagem("Erro", "Contrato não encontrado.", tipo="erro")
            return

        modalidade = contrato[11]
        if modalidade == "CLT":
            mostrar_mensagem(
                "Atenção",
                "Contratos CLT não possuem produtos associados.",
                tipo="aviso",
            )
            return

        # Chamar a visualização de produtos para este contrato
        from views.produto_pf_view import ProdutoPFView

        # Criar uma janela modal para visualização
        janela = tk.Toplevel(self.master)
        janela.title(f"Produtos do Contrato {contrato[13]}")
        janela.transient(self.master)
        janela.grab_set()

        # Maximiza a janela
        janela.state("zoomed")

        # Cria a view de produtos filtrada para este contrato
        ProdutoPFView(janela, id_contrato=id_selecao)

    def salvar_formulario(self):
        """Callback quando o formulário é salvo"""
        self.cancelar_formulario()
        self.carregar_dados()

    def cancelar_formulario(self):
        """Fecha o formulário e volta para a listagem"""
        # Remove o formulário
        if hasattr(self, "formulario"):
            self.formulario.destroy()
        self.frame_formulario.pack_forget()

        # Exibe novamente o frame principal
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
