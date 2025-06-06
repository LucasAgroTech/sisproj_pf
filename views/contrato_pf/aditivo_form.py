# Aditivo PF Form
import tkinter as tk
from tkinter import ttk

from controllers.contrato_pf_controller import buscar_contrato_por_id, atualizar_total_contrato
from controllers.aditivo_pf_controller import adicionar_aditivo
from utils.ui_utils import (
    FormularioBase,
    criar_botao,
    mostrar_mensagem,
    formatar_data,
    formatar_valor_brl,
    validar_numerico,
    converter_valor_brl_para_float,
)


class AditivoPFForm(ttk.Frame):
    """Formulário para cadastro de aditivos de contrato de pessoa física"""

    def __init__(self, master, id_contrato, callback_salvar, callback_cancelar):
        """
        Args:
            master: widget pai
            id_contrato: ID do contrato
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
        """
        super().__init__(master)
        self.master = master
        self.id_contrato = id_contrato
        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar

        # Buscar dados do contrato
        self.contrato = buscar_contrato_por_id(id_contrato)
        if not self.contrato:
            mostrar_mensagem("Erro", "Contrato não encontrado.", tipo="erro")
            self.master.destroy()
            return

        # Frame principal para organizar o layout
        self.frame_principal = ttk.Frame(self)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, pady=(0, 60))

        # Formulário para o aditivo
        self.form_aditivo = FormularioBase(self.frame_principal, "Novo Aditivo de Contrato")
        self.form_aditivo.pack(fill=tk.BOTH, expand=True)

        # Tipo de aditivo
        tipos_aditivo = ["prorrogacao", "reajuste", "ambos"]
        self.form_aditivo.adicionar_campo(
            "tipo_aditivo",
            "Tipo de Aditivo",
            tipo="opcoes",
            opcoes=tipos_aditivo,
            padrao=tipos_aditivo[0],
            required=True,
        )

        # Campo tipo_aditivo
        self.tipo_aditivo_widget = self.form_aditivo.campos["tipo_aditivo"]["widget"]

        # Ofício
        self.form_aditivo.adicionar_campo("oficio", "Ofício", padrao="", required=True)

        # Data de entrada
        self.form_aditivo.adicionar_campo(
            "data_entrada", "Data de Entrada", tipo="data", padrao="", required=True
        )
        # Formatação para data de entrada
        data_entrada_widget = self.form_aditivo.campos["data_entrada"]["widget"]
        data_entrada_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_entrada_widget, e)
        )
        data_entrada_widget.bind("<KeyPress>", validar_numerico)

        # Data de protocolo
        self.form_aditivo.adicionar_campo(
            "data_protocolo", "Data de Protocolo", tipo="data", padrao=""
        )
        # Formatação para data de protocolo
        data_protocolo_widget = self.form_aditivo.campos["data_protocolo"]["widget"]
        data_protocolo_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_protocolo_widget, e)
        )
        data_protocolo_widget.bind("<KeyPress>", validar_numerico)

        # Frame para notebook com abas específicas por tipo de aditivo
        frame_notebook = ttk.Frame(self.form_aditivo)
        frame_notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Notebook para separar os campos por tipo de aditivo
        self.notebook = ttk.Notebook(frame_notebook)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Aba de prorrogação
        self.tab_prorrogacao = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_prorrogacao, text="Prorrogação")

        # Formulário para prorrogação
        self.form_prorrogacao = FormularioBase(self.tab_prorrogacao, "")
        self.form_prorrogacao.pack(fill=tk.BOTH, expand=True)

        # Nova vigência final
        self.form_prorrogacao.adicionar_campo(
            "nova_vigencia_final",
            "Nova Vigência Final",
            tipo="data",
            padrao="",
            required=True,
        )
        # Formatação para nova vigência final
        nova_vigencia_widget = self.form_prorrogacao.campos["nova_vigencia_final"]["widget"]
        nova_vigencia_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(nova_vigencia_widget, e)
        )
        nova_vigencia_widget.bind("<KeyPress>", validar_numerico)

        # Meses adicionais
        self.form_prorrogacao.adicionar_campo(
            "meses", "Meses Adicionais", tipo="numero", padrao="", required=True
        )

        # Aba de reajuste
        self.tab_reajuste = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reajuste, text="Reajuste")

        # Formulário para reajuste
        self.form_reajuste = FormularioBase(self.tab_reajuste, "")
        self.form_reajuste.pack(fill=tk.BOTH, expand=True)

        # Remuneração atual
        remuneracao_atual = f"R$ {float(self.contrato[18]):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.form_reajuste.adicionar_campo(
            "remuneracao_atual",
            "Remuneração Atual",
            tipo="numero",
            padrao=remuneracao_atual,
            required=False,
        )
        # Configurar campo como somente leitura
        remuneracao_atual_widget = self.form_reajuste.campos["remuneracao_atual"]["widget"]
        remuneracao_atual_widget.configure(state="readonly")

        # Nova remuneração
        self.form_reajuste.adicionar_campo(
            "nova_remuneracao",
            "Nova Remuneração",
            tipo="numero",
            padrao="",
            required=True,
        )
        # Formatação para nova remuneração
        self.nova_remuneracao_widget = self.form_reajuste.campos["nova_remuneracao"]["widget"]
        self.nova_remuneracao_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(self.nova_remuneracao_widget, e)
        )
        self.nova_remuneracao_widget.bind("<FocusOut>", self.calcular_diferenca_remuneracao)

        # Diferença de remuneração
        self.form_reajuste.adicionar_campo(
            "diferenca_remuneracao",
            "Diferença de Remuneração",
            tipo="numero",
            padrao="",
            required=False,
        )
        # Configurar campo como somente leitura
        self.diferenca_widget = self.form_reajuste.campos["diferenca_remuneracao"]["widget"]
        self.diferenca_widget.configure(state="readonly")

        # Campos comuns para todos os tipos de aditivo
        frame_campos_comuns = ttk.Frame(self.form_aditivo)
        frame_campos_comuns.pack(fill=tk.X, pady=10)

        # Valor complementar
        self.form_aditivo.adicionar_campo(
            "valor_complementar", "Valor Complementar", tipo="numero", padrao=""
        )
        # Formatação para valor complementar
        valor_complementar_widget = self.form_aditivo.campos["valor_complementar"]["widget"]
        valor_complementar_widget.bind(
            "<KeyRelease>", lambda e: formatar_valor_brl(valor_complementar_widget, e)
        )

        # Responsável
        self.form_aditivo.adicionar_campo(
            "responsavel", "Responsável", padrao="", required=True
        )

        # Vincular evento de seleção do tipo de aditivo
        self.tipo_aditivo_widget.bind("<<ComboboxSelected>>", self.alternar_abas)

        # Botões de ação
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

    def alternar_abas(self, event=None):
        """Alterna as abas com base no tipo de aditivo selecionado"""
        tipo = self.tipo_aditivo_widget.get()

        if tipo == "prorrogacao":
            self.notebook.select(0)  # Seleciona a aba de prorrogação
        elif tipo == "reajuste":
            self.notebook.select(1)  # Seleciona a aba de reajuste
        elif tipo == "ambos":
            # Ambos tipos, deixa na aba atual
            pass

    def calcular_diferenca_remuneracao(self, event=None):
        """Calcula a diferença entre a remuneração atual e a nova remuneração"""
        try:
            remuneracao_atual_valor = float(self.contrato[18])
            nova_remuneracao_valor = converter_valor_brl_para_float(
                self.nova_remuneracao_widget.get()
            )

            diferenca = nova_remuneracao_valor - remuneracao_atual_valor

            self.diferenca_widget.configure(state="normal")
            self.diferenca_widget.delete(0, tk.END)
            self.diferenca_widget.insert(
                0,
                f"R$ {diferenca:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )
            self.diferenca_widget.configure(state="readonly")
        except Exception as e:
            print(f"Erro ao calcular diferença de remuneração: {e}")

    def salvar(self):
        """Salva os dados do aditivo"""
        # Validar o formulário principal
        valido, mensagem = self.form_aditivo.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return

        # Obter tipo de aditivo
        tipo_aditivo = self.tipo_aditivo_widget.get()

        # Validar formulários específicos por tipo
        if tipo_aditivo in ["prorrogacao", "ambos"]:
            valido_prorrogacao, mensagem_prorrogacao = self.form_prorrogacao.validar()
            if not valido_prorrogacao:
                mostrar_mensagem(
                    "Erro de Validação", mensagem_prorrogacao, tipo="erro"
                )
                return

        if tipo_aditivo in ["reajuste", "ambos"]:
            valido_reajuste, mensagem_reajuste = self.form_reajuste.validar()
            if not valido_reajuste:
                mostrar_mensagem(
                    "Erro de Validação", mensagem_reajuste, tipo="erro"
                )
                return

        try:
            # Obter valores do formulário principal
            valores = self.form_aditivo.obter_valores()

            # Inicializar valores específicos por tipo
            nova_vigencia_final = None
            meses = None
            nova_remuneracao = None
            diferenca_remuneracao = None

            # Obter valores específicos por tipo
            if tipo_aditivo in ["prorrogacao", "ambos"]:
                valores_prorrogacao = self.form_prorrogacao.obter_valores()
                nova_vigencia_final = valores_prorrogacao["nova_vigencia_final"]
                meses = int(valores_prorrogacao["meses"])

            if tipo_aditivo in ["reajuste", "ambos"]:
                valores_reajuste = self.form_reajuste.obter_valores()
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
            remuneracao_atual_valor = float(self.contrato[18])

            if tipo_aditivo == "prorrogacao":
                # Para prorrogação, usar a remuneração atual * meses
                valor_total_aditivo = (
                    remuneracao_atual_valor * meses
                ) + valor_complementar
            elif tipo_aditivo == "reajuste":
                # Para reajuste, pegar a diferença de remuneração * meses do contrato
                meses_contrato = int(self.contrato[16])
                valor_total_aditivo = (
                    diferenca_remuneracao * meses_contrato
                ) + valor_complementar
            elif tipo_aditivo == "ambos":
                # Para ambos, somar a nova remuneração * novos meses + diferença de remuneração * meses antigos
                meses_contrato = int(self.contrato[16])
                valor_total_aditivo = (
                    (nova_remuneracao * meses)
                    + (diferenca_remuneracao * meses_contrato)
                    + valor_complementar
                )

            # Criar o aditivo
            aditivo_id = adicionar_aditivo(
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

            # Atualizar o total do contrato
            atualizar_total_contrato(self.id_contrato)

            mostrar_mensagem(
                "Sucesso", "Aditivo adicionado com sucesso!", tipo="sucesso"
            )

            # Preparar dados para o callback
            aditivo_data = {
                "id": aditivo_id,
                "tipo_aditivo": tipo_aditivo,
                "nova_vigencia_final": nova_vigencia_final,
                "meses": meses,
                "nova_remuneracao": nova_remuneracao,
                "valor_total_aditivo": valor_total_aditivo,
            }

            # Chamar o callback de salvar
            if self.callback_salvar:
                self.callback_salvar(aditivo_data)

        except Exception as e:
            mostrar_mensagem(
                "Erro", f"Erro ao salvar aditivo: {str(e)}", tipo="erro"
            )

    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        if self.callback_cancelar:
            self.callback_cancelar()
