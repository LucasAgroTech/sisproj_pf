# Contract Form
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from controllers.contrato_pf_controller import (
    adicionar_contrato,
    buscar_contrato_por_id,
    editar_contrato,
    atualizar_total_contrato,
)
from controllers.pessoa_fisica_controller import buscar_pessoa_por_id
from controllers.demanda_controller import (
    adicionar_demanda,
    buscar_demanda_por_id,
    editar_demanda,
    listar_demandas,
)
from models.db_manager_access import get_lists_data
from utils.ui_utils import (
    FormularioBase,
    criar_botao,
    mostrar_mensagem,
    formatar_data,
    formatar_valor_brl,
    formatar_valor_brl_numerico,
    formatar_nup_sei,
    validar_numerico,
    converter_valor_brl_para_float,
)
from utils.validator import (
    validar_data,
    validar_periodo,
    calcular_meses_entre_datas,
    calcular_total_contrato,
)

from views.contrato_pf.components import PessoaFisicaSelector, ProdutosTable, AditivosTable
from views.contrato_pf.custeio_manager import CusteioManager


class ContratoPFForm(ttk.Frame):
    """Formulário para cadastro e edição de contratos de pessoa física"""

    def __init__(self, master, callback_salvar, callback_cancelar, contrato=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            contrato: dados do contrato para edição (opcional)
        """
        super().__init__(master)

        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.contrato = contrato
        self.modo_edicao = contrato is not None
        
        # Garantir que o contrato seja uma tupla ou lista válida
        if self.contrato is not None:
            if not isinstance(self.contrato, (list, tuple)):
                print(f"Aviso: contrato não é uma lista ou tupla: {type(self.contrato)}")
                self.contrato = None
                self.modo_edicao = False
                self.id_contrato = None
            elif len(self.contrato) == 0:
                print("Aviso: contrato é uma lista ou tupla vazia")
                self.contrato = None
                self.modo_edicao = False
                self.id_contrato = None
            else:
                self.id_contrato = self.contrato[0]
        else:
            self.id_contrato = None

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

        # Inicializar as abas
        self.inicializar_aba_pessoa()
        self.inicializar_aba_demanda()
        self.inicializar_aba_custeio()
        self.inicializar_aba_contrato()

        # Abas adicionais apenas para contratos existentes e que não sejam CLT
        if self.modo_edicao:
            # Verificar se a modalidade é CLT
            modalidade = self.contrato[11] if self.contrato and len(self.contrato) > 11 else None
            if modalidade != "CLT":
                self.inicializar_aba_produtos()
                self.inicializar_aba_aditivos()

        # Calcular meses e total inicial
        self.calcular_meses()
        self.calcular_total()
        
        # Forçar atualização dos valores após inicialização
        if self.modo_edicao and self.contrato:
            self.master.after(100, self.forcar_valores_contrato)
            # Recalcular total após carregar dados do contrato
            self.master.after(200, self.calcular_total)
        else:
            # Para novos contratos, garantir que o total seja calculado
            self.master.after(100, self.calcular_total)
            
    def forcar_valores_contrato(self):
        """Força a atualização dos valores do contrato nos comboboxes após inicialização"""
        try:
            if self.contrato and self.modo_edicao:
                # Modalidade
                if len(self.contrato) > 11 and self.contrato[11]:
                    self.form_contrato.campos["modalidade"]["widget"].set(self.contrato[11])
                
                # Natureza da demanda
                if len(self.contrato) > 12 and self.contrato[12]:
                    self.form_contrato.campos["natureza_demanda"]["widget"].set(self.contrato[12])
                
                # Status do contrato
                if len(self.contrato) > 17 and self.contrato[17]:
                    self.form_contrato.campos["status_contrato"]["widget"].set(self.contrato[17])

                # Lotação
                if len(self.contrato) > 24 and self.contrato[24]:
                    self.form_contrato.campos["lotacao"]["widget"].set(self.contrato[24])

                # Exercício
                if len(self.contrato) > 25 and self.contrato[25]:
                    self.form_contrato.campos["exercicio"]["widget"].set(self.contrato[25])
                
                # Solicitante na aba demanda
                if "solicitante" in self.form_demanda.campos:
                    codigo_demanda = self.contrato[1] if len(self.contrato) > 1 else None
                    demanda_encontrada = buscar_demanda_por_id(codigo_demanda) if codigo_demanda else None
                    if demanda_encontrada and len(demanda_encontrada) > 2:
                        self.form_demanda.campos["solicitante"]["widget"].set(demanda_encontrada[2])
        except Exception as e:
            print(f"Erro ao forçar valores do contrato: {e}")

    def inicializar_aba_pessoa(self):
        """Inicializa a aba de pessoa física"""
        # Aba de pessoa física (primeira aba)
        self.tab_pessoa = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pessoa, text="Pessoa Física")

        # Configurar campos na aba de pessoa física
        self.form_pessoa = FormularioBase(self.tab_pessoa, "")
        self.form_pessoa.pack(fill=tk.BOTH, expand=True)

        # Inicializar o seletor de pessoa física
        if self.modo_edicao and self.contrato and len(self.contrato) > 2:
            id_pessoa = self.contrato[2]  # ID da pessoa física
            pessoa = buscar_pessoa_por_id(id_pessoa)
            if pessoa:
                self.pessoa_selector = PessoaFisicaSelector(
                    self.form_pessoa, 
                    initial_value=pessoa[1],  # Nome completo
                    initial_id=str(pessoa[0])
                )
        else:
            self.pessoa_selector = PessoaFisicaSelector(self.form_pessoa)

    def inicializar_aba_demanda(self):
        """Inicializa a aba de demanda"""
        # Aba de demanda (segunda aba)
        self.tab_demanda = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_demanda, text="Demanda")

        # Configurar campos na aba de demanda
        self.form_demanda = FormularioBase(self.tab_demanda, "")
        self.form_demanda.pack(fill=tk.BOTH, expand=True)

        # Buscar a demanda se estiver em modo de edição
        demanda = None
        if self.modo_edicao and self.contrato and len(self.contrato) > 1:
            codigo_demanda = self.contrato[1]  # codigo_demanda
            if codigo_demanda:
                demanda = buscar_demanda_por_id(codigo_demanda)

        # Data de entrada
        self.form_demanda.adicionar_campo(
            "data_entrada",
            "Data de Entrada",
            tipo="data",
            padrao=demanda[1] if demanda and len(demanda) > 1 else "",
            required=True,
        )
        # Configurar formatação para data de entrada
        data_entrada_widget = self.form_demanda.campos["data_entrada"]["widget"]
        data_entrada_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_entrada_widget, e)
        )

        # Buscar dados da tabela lists
        lists_data = get_lists_data()

        # Lista de solicitantes
        self.form_demanda.adicionar_campo(
            "solicitante",
            "Solicitante",
            tipo="opcoes",
            opcoes=lists_data['solicitantes'],
            padrao=demanda[2] if demanda and len(demanda) > 2 else "",
            required=True,
        )

        # Data de protocolo
        self.form_demanda.adicionar_campo(
            "data_protocolo",
            "Data de Protocolo",
            tipo="data",
            padrao=demanda[3] if demanda and len(demanda) > 3 else "",
            required=True,
        )
        # Configurar formatação para data de protocolo
        data_protocolo_widget = self.form_demanda.campos["data_protocolo"]["widget"]
        data_protocolo_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_protocolo_widget, e)
        )

        # Ofício
        self.form_demanda.adicionar_campo(
            "oficio",
            "Ofício",
            padrao=demanda[4] if demanda and len(demanda) > 4 else "",
        )

        # NUP/SEI
        self.form_demanda.adicionar_campo(
            "nup_sei",
            "NUP/SEI",
            padrao=demanda[5] if demanda and len(demanda) > 5 else "",
            required=True,
        )
        # Configurar formatação para NUP/SEI
        nup_sei_widget = self.form_demanda.campos["nup_sei"]["widget"]
        nup_sei_widget.bind(
            "<KeyRelease>", lambda e: formatar_nup_sei(nup_sei_widget, e)
        )

    def inicializar_aba_custeio(self):
        """Inicializa a aba de custeio"""
        # Aba de custeio (terceira aba)
        self.tab_custeio = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_custeio, text="Custeio")

        # Configurar campos na aba de custeio
        self.form_custeio = FormularioBase(self.tab_custeio, "")
        self.form_custeio.pack(fill=tk.BOTH, expand=True)

        # Inicializar o gerenciador de custeio
        self.custeio_manager = CusteioManager(
            self.form_custeio, 
            contrato=self.contrato, 
            modo_edicao=self.modo_edicao
        )

    def inicializar_aba_contrato(self):
        """Inicializa a aba de contrato"""
        # Aba de contrato (quarta aba)
        self.tab_contrato = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_contrato, text="Contrato")

        # Configurar campos na aba de contrato
        self.form_contrato = FormularioBase(self.tab_contrato, "")
        self.form_contrato.pack(fill=tk.BOTH, expand=True)

        # Buscar dados das listas
        lists_data = get_lists_data()

        # Modalidade do contrato
        self.form_contrato.adicionar_campo(
            "modalidade",
            "Modalidade",
            tipo="opcoes",
            opcoes=lists_data['modalidades'],
            padrao=self.contrato[11] if self.contrato and len(self.contrato) > 11 else "",
            required=True,
        )

        # Natureza da demanda
        self.form_contrato.adicionar_campo(
            "natureza_demanda",
            "Natureza da Demanda",
            tipo="opcoes",
            opcoes=lists_data['naturezas'],
            padrao=self.contrato[12] if self.contrato and len(self.contrato) > 12 else "",
            required=True,
        )

        # Número do contrato
        self.form_contrato.adicionar_campo(
            "numero_contrato",
            "Número do Contrato",
            padrao=self.contrato[13] if self.contrato and len(self.contrato) > 13 else "",
            required=True,
        )

        # Lotação
        self.form_contrato.adicionar_campo(
            "lotacao",
            "Lotação",
            tipo="opcoes",
            opcoes=lists_data['lotacoes'],
            padrao=self.contrato[24] if self.contrato and len(self.contrato) > 24 else "",
            required=True,
        )

        # Exercício
        self.form_contrato.adicionar_campo(
            "exercicio",
            "Exercício",
            tipo="opcoes",
            opcoes=lists_data['exercicios'],
            padrao=self.contrato[25] if self.contrato and len(self.contrato) > 25 else "",
            required=True,
        )

        # Vigência inicial
        self.form_contrato.adicionar_campo(
            "vigencia_inicial",
            "Vigência Inicial",
            tipo="data",
            padrao=self.contrato[14] if self.contrato and len(self.contrato) > 14 else "",
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
            padrao=self.contrato[15] if self.contrato and len(self.contrato) > 15 else "",
            required=True,
        )
        # Configurar formatação para vigência final
        vigencia_final_widget = self.form_contrato.campos["vigencia_final"]["widget"]
        vigencia_final_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(vigencia_final_widget, e)
        )
        vigencia_final_widget.bind("<FocusOut>", self.calcular_meses)

        # Meses
        meses_padrao = self.contrato[16] if self.contrato and len(self.contrato) > 16 else ""
        self.form_contrato.adicionar_campo(
            "meses", "Meses", tipo="numero", padrao=meses_padrao, required=True
        )
        # Configurar recálculo quando o campo de meses for alterado
        meses_widget = self.form_contrato.campos["meses"]["widget"]
        meses_widget.bind("<KeyPress>", validar_numerico)

        # Status do contrato
        self.form_contrato.adicionar_campo(
            "status_contrato",
            "Status do Contrato",
            tipo="opcoes",
            opcoes=lists_data['status'],
            padrao=self.contrato[17] if self.contrato and len(self.contrato) > 17 else "",
            required=True,
        )

        # Remuneração
        remuneracao_padrao = (
            formatar_valor_brl_numerico(float(self.contrato[18])) if self.contrato and len(self.contrato) > 18 and self.contrato[18] is not None else ""
        )
        self.form_contrato.adicionar_campo(
            "remuneracao",
            "Remuneração",
            tipo="texto",  # Alterado para texto para manter a formatação
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
            bool(self.contrato[19]) if self.contrato and len(self.contrato) > 19 else False
        )
        self.form_contrato.adicionar_campo(
            "intersticio",
            "Interstício",
            tipo="checkbox",
            padrao=intersticio_padrao,
        )
        # Configurar recálculo quando o checkbox de interstício for alterado
        intersticio_widget = self.form_contrato.campos["intersticio"]["widget"]
        intersticio_widget.bind("<ButtonRelease-1>", self.calcular_total)

        # Valor do interstício
        valor_intersticio_padrao = (
            formatar_valor_brl_numerico(float(self.contrato[20])) if self.contrato and len(self.contrato) > 20 and self.contrato[20] is not None else ""
        )
        self.form_contrato.adicionar_campo(
            "valor_intersticio",
            "Valor do Interstício",
            tipo="texto",  # Alterado para texto para manter a formatação
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
            formatar_valor_brl_numerico(float(self.contrato[21])) if self.contrato and len(self.contrato) > 21 and self.contrato[21] is not None else ""
        )
        self.form_contrato.adicionar_campo(
            "valor_complementar",
            "Valor Complementar",
            tipo="texto",  # Alterado para texto para manter a formatação
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
        total_contrato_padrao = (
            formatar_valor_brl_numerico(float(self.contrato[22])) if self.contrato and len(self.contrato) > 22 and self.contrato[22] is not None else ""
        )
        self.form_contrato.adicionar_campo(
            "total_contrato",
            "Total do Contrato",
            tipo="texto",  # Alterado para texto para manter a formatação
            padrao=total_contrato_padrao,
            required=True,
        )
        # Configurar formatação para total do contrato
        total_contrato_widget = self.form_contrato.campos["total_contrato"]["widget"]
        total_contrato_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(total_contrato_widget, e)
        )

        # Observações
        observacoes_padrao = self.contrato[23] if self.contrato and len(self.contrato) > 23 else ""
        self.form_contrato.adicionar_campo(
            "observacoes", "Observações", tipo="texto_longo", padrao=observacoes_padrao
        )

    def inicializar_aba_produtos(self):
        """Inicializa a aba de produtos (apenas para contratos existentes)"""
        # Aba de produtos (quinta aba)
        self.tab_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_produtos, text="Produtos")

        # Obter a modalidade do contrato
        modalidade = self.contrato[11] if self.contrato and len(self.contrato) > 11 else None

        # Inicializar a tabela de produtos
        self.produtos_table = ProdutosTable(
            self.tab_produtos,
            id_contrato=self.id_contrato,
            modalidade=modalidade
        )

    def inicializar_aba_aditivos(self):
        """Inicializa a aba de aditivos (apenas para contratos existentes)"""
        # Aba de aditivos (sexta aba)
        self.tab_aditivos = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_aditivos, text="Aditivos")

        # Inicializar a tabela de aditivos
        self.aditivos_table = AditivosTable(
            self.tab_aditivos,
            id_contrato=self.id_contrato,
            callback_aditivo_added=self.atualizar_contrato_apos_aditivo
        )

    def atualizar_contrato_apos_aditivo(self, aditivo_data):
        """Atualiza os campos do contrato após adicionar ou excluir um aditivo"""
        if not aditivo_data:  # Caso de exclusão
            # Recarregar os dados do contrato
            contrato = buscar_contrato_por_id(self.id_contrato)
            if contrato:
                # Atualizar os campos do formulário
                self.form_contrato.campos["total_contrato"]["widget"].delete(0, tk.END)
                self.form_contrato.campos["total_contrato"]["widget"].insert(
                    0,
                    f"R$ {float(contrato[22]):,.2f}".replace(",", "X")
                    .replace(".", ",")
                    .replace("X", "."),
                )

                # Atualizar outros campos relevantes
                self.form_contrato.campos["vigencia_final"]["widget"].delete(0, tk.END)
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
            return

        # Caso de adição
        tipo_aditivo = aditivo_data.get("tipo_aditivo")
        
        if tipo_aditivo in ["prorrogacao", "ambos"]:
            # Atualizar vigência final e meses
            nova_vigencia_final = aditivo_data.get("nova_vigencia_final")
            meses = aditivo_data.get("meses", 0)
            
            self.form_contrato.campos["vigencia_final"]["widget"].delete(0, tk.END)
            self.form_contrato.campos["vigencia_final"]["widget"].insert(
                0, nova_vigencia_final
            )

            # Atualizar meses (somar os novos meses)
            meses_contrato = int(self.form_contrato.campos["meses"]["widget"].get() or 0)
            self.form_contrato.campos["meses"]["widget"].delete(0, tk.END)
            self.form_contrato.campos["meses"]["widget"].insert(
                0, str(meses_contrato + meses)
            )

        if tipo_aditivo in ["reajuste", "ambos"]:
            # Atualizar remuneração
            nova_remuneracao = aditivo_data.get("nova_remuneracao", 0)
            self.form_contrato.campos["remuneracao"]["widget"].delete(0, tk.END)
            self.form_contrato.campos["remuneracao"]["widget"].insert(
                0,
                f"R$ {nova_remuneracao:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )

        # Atualizar total do contrato
        contrato = buscar_contrato_por_id(self.id_contrato)
        if contrato:
            self.form_contrato.campos["total_contrato"]["widget"].delete(0, tk.END)
            self.form_contrato.campos["total_contrato"]["widget"].insert(
                0,
                f"R$ {float(contrato[22]):,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )

    def _on_valor_change(self, widget, event):
        """Formata valores monetários e programa recálculo do total"""
        formatar_valor_brl(widget, event)
        # Programa recálculo com delay para evitar muitos cálculos durante a digitação
        self.master.after(500, self.calcular_total)

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
        """Calcula o total do contrato"""
        try:
            # Obter valores dos campos
            remuneracao = self.form_contrato.campos["remuneracao"]["widget"].get().strip()
            meses = self.form_contrato.campos["meses"]["widget"].get().strip()
            valor_intersticio = self.form_contrato.campos["valor_intersticio"]["widget"].get().strip()
            valor_complementar = self.form_contrato.campos["valor_complementar"]["widget"].get().strip()
            
            # Converter valores monetários
            remuneracao = converter_valor_brl_para_float(remuneracao) if remuneracao else 0
            meses = int(meses) if meses else 0
            valor_intersticio = converter_valor_brl_para_float(valor_intersticio) if valor_intersticio else 0
            valor_complementar = converter_valor_brl_para_float(valor_complementar) if valor_complementar else 0
            
            # Verificar se tem interstício marcado
            tem_intersticio = self.form_contrato.campos["intersticio"]["widget"].get()
            if not tem_intersticio:
                valor_intersticio = 0
            
            # Calcular total
            total = (remuneracao * meses) + valor_intersticio + valor_complementar
            
            # Atualizar campo de total
            self.form_contrato.campos["total_contrato"]["widget"].delete(0, tk.END)
            self.form_contrato.campos["total_contrato"]["widget"].insert(0, formatar_valor_brl(total))
            
        except Exception as e:
            print(f"Erro ao calcular total: {e}")
            # Em caso de erro, limpa o campo total
            self.form_contrato.campos["total_contrato"]["widget"].delete(0, tk.END)

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
            id_pessoa = self.pessoa_selector.get_id()
            if not id_pessoa:
                mostrar_mensagem(
                    "Erro de Validação", "Selecione uma pessoa física.", tipo="erro"
                )
                return

            # Obter valores do formulário
            valores_contrato = self.form_contrato.obter_valores()
            valores_custeio = self.form_custeio.obter_valores()

            # Converter valores
            remuneracao = converter_valor_brl_para_float(valores_contrato["remuneracao"])
            valor_intersticio = converter_valor_brl_para_float(
                valores_contrato["valor_intersticio"]
            )
            valor_complementar = converter_valor_brl_para_float(
                valores_contrato["valor_complementar"]
            )

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

            if self.modo_edicao:
                # Editar contrato existente
                valores_demanda = self.form_demanda.obter_valores()

                # Editar demanda
                editar_demanda(
                    self.contrato[1],
                    valores_demanda["data_entrada"],
                    valores_demanda["solicitante"],
                    valores_demanda["data_protocolo"],
                    valores_demanda["oficio"],
                    valores_demanda["nup_sei"],
                )

                # Obter código da demanda
                codigo_demanda = self.contrato[1]

                # Converter valores
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
                    valores_contrato["lotacao"],
                    valores_contrato["exercicio"],
                )

                mostrar_mensagem(
                    "Sucesso", "Contrato atualizado com sucesso!", tipo="sucesso"
                )
            else:
                # Cadastrar nova demanda
                valores_demanda = self.form_demanda.obter_valores()

                # Criar a demanda
                adicionar_demanda(
                    valores_demanda["data_entrada"],
                    valores_demanda["solicitante"],
                    valores_demanda["data_protocolo"],
                    valores_demanda["oficio"],
                    valores_demanda["nup_sei"],
                )

                # Obter o código da nova demanda (última demanda inserida)
                demandas = listar_demandas()
                codigo_demanda = demandas[-1][0] if demandas else 1

                # Obter valores do contrato
                valores_contrato = self.form_contrato.obter_valores()
                valores_custeio = self.form_custeio.obter_valores()

                # Converter valores
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
                    valores_contrato["lotacao"],
                    valores_contrato["exercicio"],
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
