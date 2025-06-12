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

        # Tipo de aditivo - ALTERADO
        tipos_aditivo = ["TEMPO E VALOR", "TEMPO", "VALOR"]
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

        # Ofício - NÃO OBRIGATÓRIO
        self.form_aditivo.adicionar_campo("oficio", "Ofício", padrao="", required=False)

        # Data de entrada - NÃO OBRIGATÓRIA
        self.form_aditivo.adicionar_campo(
            "data_entrada", "Data de Entrada", tipo="data", padrao="", required=False
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

        # DADOS ORIGINAIS DO CONTRATO
        self.frame_dados_originais = ttk.LabelFrame(self.form_aditivo, text="Dados Originais do Contrato")
        self.frame_dados_originais.pack(fill=tk.X, pady=10)

        # Primeira linha - Nome da pessoa física
        frame_linha0 = ttk.Frame(self.frame_dados_originais)
        frame_linha0.pack(fill=tk.X, pady=2)

        ttk.Label(frame_linha0, text="Pessoa Física:").grid(row=0, column=0, sticky="w", padx=5)
        self.nome_pessoa_entry = ttk.Entry(frame_linha0, state="readonly")
        self.nome_pessoa_entry.grid(row=0, column=1, sticky="ew", padx=5)

        frame_linha0.columnconfigure(1, weight=1)

        # Segunda linha - Número do contrato e modalidade
        frame_linha1 = ttk.Frame(self.frame_dados_originais)
        frame_linha1.pack(fill=tk.X, pady=2)

        ttk.Label(frame_linha1, text="Número do Contrato:").grid(row=0, column=0, sticky="w", padx=5)
        self.numero_contrato_original_entry = ttk.Entry(frame_linha1, state="readonly")
        self.numero_contrato_original_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame_linha1, text="Modalidade:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.modalidade_original_entry = ttk.Entry(frame_linha1, state="readonly")
        self.modalidade_original_entry.grid(row=0, column=3, sticky="ew", padx=5)

        frame_linha1.columnconfigure(1, weight=1)
        frame_linha1.columnconfigure(3, weight=1)

        # Terceira linha - Vigências
        frame_linha2 = ttk.Frame(self.frame_dados_originais)
        frame_linha2.pack(fill=tk.X, pady=2)

        ttk.Label(frame_linha2, text="Vigência Inicial:").grid(row=0, column=0, sticky="w", padx=5)
        self.vigencia_inicial_original_entry = ttk.Entry(frame_linha2, state="readonly")
        self.vigencia_inicial_original_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame_linha2, text="Vigência Final Original:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.vigencia_final_original_entry = ttk.Entry(frame_linha2, state="readonly")
        self.vigencia_final_original_entry.grid(row=0, column=3, sticky="ew", padx=5)

        frame_linha2.columnconfigure(1, weight=1)
        frame_linha2.columnconfigure(3, weight=1)

        # Quarta linha - Meses e remuneração
        frame_linha3 = ttk.Frame(self.frame_dados_originais)
        frame_linha3.pack(fill=tk.X, pady=2)

        ttk.Label(frame_linha3, text="Meses Originais:").grid(row=0, column=0, sticky="w", padx=5)
        self.meses_originais_entry = ttk.Entry(frame_linha3, state="readonly")
        self.meses_originais_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        ttk.Label(frame_linha3, text="Remuneração Original:").grid(row=0, column=2, sticky="w", padx=(20, 5))
        self.remuneracao_original_entry = ttk.Entry(frame_linha3, state="readonly")
        self.remuneracao_original_entry.grid(row=0, column=3, sticky="ew", padx=5)

        frame_linha3.columnconfigure(1, weight=1)
        frame_linha3.columnconfigure(3, weight=1)

        # Quinta linha - Valor total original
        frame_linha4 = ttk.Frame(self.frame_dados_originais)
        frame_linha4.pack(fill=tk.X, pady=2)

        ttk.Label(frame_linha4, text="Valor Total Original:").grid(row=0, column=0, sticky="w", padx=5)
        self.valor_total_original_entry = ttk.Entry(frame_linha4, state="readonly")
        self.valor_total_original_entry.grid(row=0, column=1, sticky="ew", padx=5)

        frame_linha4.columnconfigure(1, weight=1)

        # Preencher dados originais do contrato
        self.preencher_dados_originais()

        # Frame para campos condicionais
        self.frame_campos_condicionais = ttk.LabelFrame(self.form_aditivo, text="Dados do Aditivo")
        self.frame_campos_condicionais.pack(fill=tk.BOTH, expand=True, pady=10)

        # CAMPOS PARA EXTENSÃO DE TEMPO
        self.frame_tempo = ttk.Frame(self.frame_campos_condicionais)
        self.frame_tempo.pack(fill=tk.X, pady=5)

        # Nova vigência final
        ttk.Label(self.frame_tempo, text="Nova Vigência Final (Após Aditivo):").grid(row=0, column=0, sticky="w", padx=5)
        self.nova_vigencia_entry = ttk.Entry(self.frame_tempo)
        self.nova_vigencia_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.nova_vigencia_entry.bind("<KeyRelease>", self.on_nova_vigencia_change)
        self.nova_vigencia_entry.bind("<KeyPress>", validar_numerico)
        self.nova_vigencia_entry.bind("<FocusOut>", self.calcular_meses_adicionais)

        # Meses adicionais (calculado automaticamente)
        ttk.Label(self.frame_tempo, text="Meses Adicionais:").grid(row=1, column=0, sticky="w", padx=5)
        self.meses_entry = ttk.Entry(self.frame_tempo, state="readonly")
        self.meses_entry.grid(row=1, column=1, sticky="ew", padx=5)

        self.frame_tempo.columnconfigure(1, weight=1)

        # CAMPOS PARA REAJUSTE DE VALOR
        self.frame_valor = ttk.Frame(self.frame_campos_condicionais)
        self.frame_valor.pack(fill=tk.X, pady=5)

        # Remuneração atual (somente leitura)
        ttk.Label(self.frame_valor, text="Remuneração Atual:").grid(row=0, column=0, sticky="w", padx=5)
        self.remuneracao_atual_entry = ttk.Entry(self.frame_valor, state="readonly")
        self.remuneracao_atual_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Definir valor da remuneração atual
        try:
            valor_remuneracao = float(self.contrato[18] or 0)
            remuneracao_atual = f"R$ {valor_remuneracao:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, IndexError):
            remuneracao_atual = "R$ 0,00"
        
        self.remuneracao_atual_entry.configure(state="normal")
        self.remuneracao_atual_entry.insert(0, remuneracao_atual)
        self.remuneracao_atual_entry.configure(state="readonly")

        # Nova remuneração
        ttk.Label(self.frame_valor, text="Nova Remuneração:").grid(row=1, column=0, sticky="w", padx=5)
        self.nova_remuneracao_entry = ttk.Entry(self.frame_valor)
        self.nova_remuneracao_entry.grid(row=1, column=1, sticky="ew", padx=5)
        self.nova_remuneracao_entry.bind("<KeyRelease>", self.on_nova_remuneracao_change)
        self.nova_remuneracao_entry.bind("<FocusOut>", self.calcular_diferenca_remuneracao)

        # Data de início da nova remuneração
        ttk.Label(self.frame_valor, text="Data Início Nova Remuneração:").grid(row=2, column=0, sticky="w", padx=5)
        self.data_inicio_nova_remuneracao_entry = ttk.Entry(self.frame_valor)
        self.data_inicio_nova_remuneracao_entry.grid(row=2, column=1, sticky="ew", padx=5)
        self.data_inicio_nova_remuneracao_entry.bind("<KeyRelease>", self.on_data_inicio_change)
        self.data_inicio_nova_remuneracao_entry.bind("<KeyPress>", validar_numerico)
        self.data_inicio_nova_remuneracao_entry.bind("<FocusOut>", self.calcular_valores_aditivo)

        # Diferença de remuneração (calculado automaticamente)
        ttk.Label(self.frame_valor, text="Diferença de Remuneração:").grid(row=3, column=0, sticky="w", padx=5)
        self.diferenca_entry = ttk.Entry(self.frame_valor, state="readonly")
        self.diferenca_entry.grid(row=3, column=1, sticky="ew", padx=5)

        self.frame_valor.columnconfigure(1, weight=1)

        # VALOR COMPLEMENTAR
        self.frame_complementar = ttk.Frame(self.frame_campos_condicionais)
        self.frame_complementar.pack(fill=tk.X, pady=5)

        ttk.Label(self.frame_complementar, text="Valor Complementar:").grid(row=0, column=0, sticky="w", padx=5)
        self.valor_complementar_entry = ttk.Entry(self.frame_complementar)
        self.valor_complementar_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.valor_complementar_entry.bind("<KeyRelease>", self.on_valor_complementar_change)
        self.valor_complementar_entry.bind("<FocusOut>", self.calcular_valores_aditivo)

        self.frame_complementar.columnconfigure(1, weight=1)

        # RESUMO DO ADITIVO
        self.frame_resumo = ttk.LabelFrame(self.frame_campos_condicionais, text="Resumo do Aditivo")
        self.frame_resumo.pack(fill=tk.X, pady=5)

        # Valor total atual do contrato (somente leitura)
        ttk.Label(self.frame_resumo, text="Valor Total Atual do Contrato:").grid(row=0, column=0, sticky="w", padx=5)
        self.valor_atual_contrato_entry = ttk.Entry(self.frame_resumo, state="readonly")
        self.valor_atual_contrato_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Definir valor atual do contrato
        try:
            valor_total = float(self.contrato[22] or 0)
            valor_atual = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, IndexError):
            valor_atual = "R$ 0,00"
            
        self.valor_atual_contrato_entry.configure(state="normal")
        self.valor_atual_contrato_entry.insert(0, valor_atual)
        self.valor_atual_contrato_entry.configure(state="readonly")

        # Valor do aditivo (calculado automaticamente)
        ttk.Label(self.frame_resumo, text="Valor do Aditivo:").grid(row=1, column=0, sticky="w", padx=5)
        self.valor_aditivo_entry = ttk.Entry(self.frame_resumo, state="readonly")
        self.valor_aditivo_entry.grid(row=1, column=1, sticky="ew", padx=5)

        # Valor total do contrato após o aditivo (calculado automaticamente)
        ttk.Label(self.frame_resumo, text="Valor Total Após Aditivo:").grid(row=2, column=0, sticky="w", padx=5)
        self.valor_total_pos_aditivo_entry = ttk.Entry(self.frame_resumo, state="readonly")
        self.valor_total_pos_aditivo_entry.grid(row=2, column=1, sticky="ew", padx=5)

        self.frame_resumo.columnconfigure(1, weight=1)

        # Vincular evento de seleção do tipo de aditivo
        self.tipo_aditivo_widget.bind("<<ComboboxSelected>>", self.configurar_campos_por_tipo)

        # Configurar campos iniciais
        self.configurar_campos_por_tipo()
        
        # Calcular valores iniciais
        self.calcular_valores_aditivo()

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

    def preencher_dados_originais(self):
        """Preenche os campos com os dados originais do contrato"""
        try:
            if not self.contrato or len(self.contrato) < 23:
                return

            # Nome da pessoa física (último índice - resultado do JOIN)
            nome_pessoa = self.contrato[-1] or ""
            self.nome_pessoa_entry.configure(state="normal")
            self.nome_pessoa_entry.insert(0, nome_pessoa)
            self.nome_pessoa_entry.configure(state="readonly")

            # Número do contrato (índice 13)
            numero_contrato = self.contrato[13] or ""
            self.numero_contrato_original_entry.configure(state="normal")
            self.numero_contrato_original_entry.insert(0, numero_contrato)
            self.numero_contrato_original_entry.configure(state="readonly")

            # Modalidade (índice 11)
            modalidade = self.contrato[11] or ""
            self.modalidade_original_entry.configure(state="normal")
            self.modalidade_original_entry.insert(0, modalidade)
            self.modalidade_original_entry.configure(state="readonly")

            # Vigência inicial (índice 14) - Converter de YYYY-MM-DD para DD/MM/YYYY
            vigencia_inicial = self.contrato[14] or ""
            if vigencia_inicial:
                try:
                    from datetime import datetime
                    data_obj = datetime.strptime(vigencia_inicial, "%Y-%m-%d")
                    vigencia_inicial = data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    pass  # Manter formato original se não conseguir converter
            
            self.vigencia_inicial_original_entry.configure(state="normal")
            self.vigencia_inicial_original_entry.insert(0, vigencia_inicial)
            self.vigencia_inicial_original_entry.configure(state="readonly")

            # Vigência final original (índice 15) - Converter de YYYY-MM-DD para DD/MM/YYYY
            vigencia_final = self.contrato[15] or ""
            if vigencia_final:
                try:
                    from datetime import datetime
                    data_obj = datetime.strptime(vigencia_final, "%Y-%m-%d")
                    vigencia_final = data_obj.strftime("%d/%m/%Y")
                except ValueError:
                    pass  # Manter formato original se não conseguir converter
            
            self.vigencia_final_original_entry.configure(state="normal")
            self.vigencia_final_original_entry.insert(0, vigencia_final)
            self.vigencia_final_original_entry.configure(state="readonly")

            # Meses originais (índice 16)
            meses_originais = self.contrato[16] or 0
            self.meses_originais_entry.configure(state="normal")
            self.meses_originais_entry.insert(0, str(meses_originais))
            self.meses_originais_entry.configure(state="readonly")

            # Remuneração original (índice 18)
            try:
                remuneracao_valor = float(self.contrato[18] or 0)
                remuneracao_formatada = f"R$ {remuneracao_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                remuneracao_formatada = "R$ 0,00"
            
            self.remuneracao_original_entry.configure(state="normal")
            self.remuneracao_original_entry.insert(0, remuneracao_formatada)
            self.remuneracao_original_entry.configure(state="readonly")

            # Valor total original (índice 22)
            try:
                valor_total_valor = float(self.contrato[22] or 0)
                valor_total_formatado = f"R$ {valor_total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                valor_total_formatado = "R$ 0,00"
            
            self.valor_total_original_entry.configure(state="normal")
            self.valor_total_original_entry.insert(0, valor_total_formatado)
            self.valor_total_original_entry.configure(state="readonly")

        except Exception as e:
            # Em caso de erro, deixar campos vazios
            pass

    def configurar_campos_por_tipo(self, event=None):
        """Configura quais campos devem estar habilitados baseado no tipo de aditivo"""
        tipo = self.tipo_aditivo_widget.get()

        # Desabilitar todos os campos primeiro
        self.nova_vigencia_entry.configure(state="disabled")
        self.meses_entry.configure(state="readonly")
        self.nova_remuneracao_entry.configure(state="disabled")
        self.data_inicio_nova_remuneracao_entry.configure(state="disabled")
        self.diferenca_entry.configure(state="readonly")
        self.valor_complementar_entry.configure(state="disabled")

        if tipo == "TEMPO E VALOR":
            # Habilitar todos os campos
            self.nova_vigencia_entry.configure(state="normal")
            self.nova_remuneracao_entry.configure(state="normal")
            self.data_inicio_nova_remuneracao_entry.configure(state="normal")
            self.valor_complementar_entry.configure(state="normal")
        elif tipo == "TEMPO":
            # Habilitar apenas campos de tempo
            self.nova_vigencia_entry.configure(state="normal")
            self.valor_complementar_entry.configure(state="normal")
        elif tipo == "VALOR":
            # Habilitar apenas campos de valor
            self.nova_remuneracao_entry.configure(state="normal")
            self.data_inicio_nova_remuneracao_entry.configure(state="normal")
            self.valor_complementar_entry.configure(state="normal")
            
        # Recalcular valores após mudança de tipo
        self.calcular_valores_aditivo()

    def on_nova_vigencia_change(self, event=None):
        """Evento ao mudar nova vigência - formatar data e calcular meses"""
        # Primeiro formatar a data
        formatar_data(self.nova_vigencia_entry, event)
        # Depois calcular meses adicionais
        self.calcular_meses_adicionais()

    def on_nova_remuneracao_change(self, event=None):
        """Evento ao mudar nova remuneração - formatar valor e calcular diferença"""
        # Primeiro formatar o valor
        formatar_valor_brl(self.nova_remuneracao_entry, event)
        # Depois calcular diferença de remuneração
        self.calcular_diferenca_remuneracao()

    def on_data_inicio_change(self, event=None):
        """Evento ao mudar data de início - formatar data e recalcular valores"""
        # Primeiro formatar a data
        formatar_data(self.data_inicio_nova_remuneracao_entry, event)
        # Depois recalcular valores
        self.calcular_valores_aditivo()

    def on_valor_complementar_change(self, event=None):
        """Evento ao mudar valor complementar - formatar valor e recalcular"""
        # Primeiro formatar o valor
        formatar_valor_brl(self.valor_complementar_entry, event)
        # Depois recalcular valores
        self.calcular_valores_aditivo()

    def calcular_meses_adicionais(self, event=None):
        """Calcula automaticamente os meses adicionais baseado na nova vigência"""
        try:
            nova_vigencia = self.nova_vigencia_entry.get().strip()
            if not nova_vigencia or len(nova_vigencia) != 10:
                # Limpar campo de meses se data não estiver completa
                self.meses_entry.configure(state="normal")
                self.meses_entry.delete(0, tk.END)
                self.meses_entry.configure(state="readonly")
                return

            # Converter datas para calcular diferença
            from datetime import datetime
            
            # Data final atual do contrato (índice 15 baseado na estrutura do contrato)
            vigencia_atual = self.contrato[15]  # vigencia_final no formato YYYY-MM-DD
            
            # Converter strings de data para objetos datetime
            data_atual = datetime.strptime(vigencia_atual, "%Y-%m-%d")
            
            # A nova vigência vem no formato DD/MM/YYYY
            data_nova = datetime.strptime(nova_vigencia, "%d/%m/%Y")
            
            # Calcular diferença em meses
            diferenca_anos = data_nova.year - data_atual.year
            diferenca_meses = data_nova.month - data_atual.month
            total_meses = diferenca_anos * 12 + diferenca_meses
            
            # Ajustar se a nova data é menor que a atual
            if data_nova.day < data_atual.day:
                total_meses -= 1
            
            # Atualizar campo de meses
            self.meses_entry.configure(state="normal")
            self.meses_entry.delete(0, tk.END)
            self.meses_entry.insert(0, str(max(0, total_meses)))
            self.meses_entry.configure(state="readonly")
            
            # Recalcular valores do aditivo
            self.calcular_valores_aditivo()
            
        except Exception as e:
            # Limpar campo de meses em caso de erro
            self.meses_entry.configure(state="normal")
            self.meses_entry.delete(0, tk.END)
            self.meses_entry.configure(state="readonly")

    def calcular_diferenca_remuneracao(self, event=None):
        """Calcula a diferença entre a remuneração atual e a nova remuneração"""
        try:
            remuneracao_atual_valor = float(self.contrato[18])
            nova_remuneracao_str = self.nova_remuneracao_entry.get().strip()
            
            if not nova_remuneracao_str or nova_remuneracao_str in ["R$", "R$ "]:
                # Limpar campo de diferença se não há valor válido
                self.diferenca_entry.configure(state="normal")
                self.diferenca_entry.delete(0, tk.END)
                self.diferenca_entry.configure(state="readonly")
                return
                
            nova_remuneracao_valor = converter_valor_brl_para_float(nova_remuneracao_str)

            diferenca = nova_remuneracao_valor - remuneracao_atual_valor

            self.diferenca_entry.configure(state="normal")
            self.diferenca_entry.delete(0, tk.END)
            self.diferenca_entry.insert(
                0,
                f"R$ {diferenca:,.2f}".replace(",", "X")
                .replace(".", ",")
                .replace("X", "."),
            )
            self.diferenca_entry.configure(state="readonly")
            
            # Recalcular valores do aditivo
            self.calcular_valores_aditivo()
            
        except Exception as e:
            # Limpar campo de diferença em caso de erro
            self.diferenca_entry.configure(state="normal")
            self.diferenca_entry.delete(0, tk.END)
            self.diferenca_entry.configure(state="readonly")

    def calcular_valores_aditivo(self, event=None):
        """Calcula automaticamente os valores do aditivo e o total após o aditivo"""
        try:
            tipo_aditivo = self.tipo_aditivo_widget.get()
            
            if not tipo_aditivo:
                return
            
            # Verificar se o contrato foi carregado corretamente
            if not self.contrato or len(self.contrato) < 23:
                return
            
            # Valores básicos do contrato
            remuneracao_atual = float(self.contrato[18] or 0)
            meses_contrato_original = int(self.contrato[16] or 0)
            valor_atual_contrato = float(self.contrato[22] or 0)
            vigencia_final_original = self.contrato[15]  # YYYY-MM-DD
            
            # Inicializar variáveis
            valor_aditivo = 0
            meses_adicionais = 0
            nova_remuneracao = 0
            diferenca_remuneracao = 0
            valor_complementar = 0
            
            # Obter valor complementar
            try:
                valor_complementar_str = self.valor_complementar_entry.get().strip()
                if valor_complementar_str and valor_complementar_str not in ["R$", "R$ ", ""]:
                    valor_complementar = converter_valor_brl_para_float(valor_complementar_str)
                else:
                    valor_complementar = 0
            except Exception as e:
                valor_complementar = 0
            
            # Calcular baseado no tipo de aditivo
            if tipo_aditivo == "TEMPO":
                # Apenas extensão de tempo - usar remuneração atual
                meses_str = self.meses_entry.get().strip()
                if meses_str:
                    try:
                        meses_adicionais = int(meses_str)
                        # Valor do aditivo = remuneração atual * meses adicionais + valor complementar
                        valor_aditivo = (remuneracao_atual * meses_adicionais) + valor_complementar
                    except ValueError as e:
                        pass
                    
            elif tipo_aditivo == "VALOR":
                # Apenas reajuste de valor - calcular meses restantes considerando data de início
                nova_remuneracao_str = self.nova_remuneracao_entry.get().strip()
                data_inicio_str = self.data_inicio_nova_remuneracao_entry.get().strip()
                
                if nova_remuneracao_str and nova_remuneracao_str not in ["R$", "R$ ", ""]:
                    try:
                        nova_remuneracao = converter_valor_brl_para_float(nova_remuneracao_str)
                        diferenca_remuneracao = nova_remuneracao - remuneracao_atual
                        
                        # Calcular meses desde a data de início até o fim do contrato
                        meses_restantes = meses_contrato_original
                        
                        if data_inicio_str and len(data_inicio_str) == 10:
                            try:
                                from datetime import datetime
                                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
                                data_fim_contrato = datetime.strptime(vigencia_final_original, "%Y-%m-%d")
                                
                                # Calcular meses entre data de início da nova remuneração e fim do contrato
                                diferenca_anos = data_fim_contrato.year - data_inicio.year
                                diferenca_meses = data_fim_contrato.month - data_inicio.month
                                meses_restantes = diferenca_anos * 12 + diferenca_meses
                                
                                # Ajustar se o dia final é menor que o inicial
                                if data_fim_contrato.day < data_inicio.day:
                                    meses_restantes -= 1
                                    
                                meses_restantes = max(0, meses_restantes)
                            except Exception:
                                pass  # Usar meses originais em caso de erro
                        
                        # Valor do aditivo = diferença * meses restantes + valor complementar
                        valor_aditivo = (diferenca_remuneracao * meses_restantes) + valor_complementar
                        
                    except Exception as e:
                        pass
                    
            elif tipo_aditivo == "TEMPO E VALOR":
                # Extensão de tempo e reajuste de valor
                meses_str = self.meses_entry.get().strip()
                nova_remuneracao_str = self.nova_remuneracao_entry.get().strip()
                data_inicio_str = self.data_inicio_nova_remuneracao_entry.get().strip()
                
                if meses_str and nova_remuneracao_str and nova_remuneracao_str not in ["R$", "R$ ", ""]:
                    try:
                        meses_adicionais = int(meses_str)
                        nova_remuneracao = converter_valor_brl_para_float(nova_remuneracao_str)
                        diferenca_remuneracao = nova_remuneracao - remuneracao_atual
                        
                        # Para TEMPO E VALOR, temos duas possibilidades:
                        # 1. Se há data de início, aplicar nova remuneração a partir dessa data
                        # 2. Se não há data de início, aplicar nova remuneração apenas aos meses adicionais
                        
                        if data_inicio_str and len(data_inicio_str) == 10:
                            try:
                                from datetime import datetime
                                data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y")
                                data_fim_original = datetime.strptime(vigencia_final_original, "%Y-%m-%d")
                                
                                # Calcular meses desde data de início até fim original
                                diferenca_anos = data_fim_original.year - data_inicio.year
                                diferenca_meses = data_fim_original.month - data_inicio.month
                                meses_desde_inicio = diferenca_anos * 12 + diferenca_meses
                                
                                if data_fim_original.day < data_inicio.day:
                                    meses_desde_inicio -= 1
                                    
                                meses_desde_inicio = max(0, meses_desde_inicio)
                                
                                # Valor = (diferença * meses desde início até fim original) + (nova remuneração * meses adicionais)
                                valor_aditivo = (diferenca_remuneracao * meses_desde_inicio) + (nova_remuneracao * meses_adicionais) + valor_complementar
                                
                            except Exception:
                                # Fallback: nova remuneração apenas nos meses adicionais
                                valor_aditivo = (nova_remuneracao * meses_adicionais) + valor_complementar
                        else:
                            # Sem data de início específica: nova remuneração apenas nos meses adicionais
                            valor_aditivo = (nova_remuneracao * meses_adicionais) + valor_complementar
                            
                    except Exception as e:
                        pass
            
            # Atualizar campos de resumo
            self.valor_aditivo_entry.configure(state="normal")
            self.valor_aditivo_entry.delete(0, tk.END)
            self.valor_aditivo_entry.insert(0, f"R$ {valor_aditivo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.valor_aditivo_entry.configure(state="readonly")
            
            # Calcular valor total após aditivo
            valor_total_pos_aditivo = valor_atual_contrato + valor_aditivo
            
            self.valor_total_pos_aditivo_entry.configure(state="normal")
            self.valor_total_pos_aditivo_entry.delete(0, tk.END)
            self.valor_total_pos_aditivo_entry.insert(0, f"R$ {valor_total_pos_aditivo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.valor_total_pos_aditivo_entry.configure(state="readonly")
            
        except Exception as e:
            # Em caso de erro, manter valores zerados
            pass

    def salvar(self):
        """Salva os dados do aditivo"""
        # Validar o formulário principal
        valido, mensagem = self.form_aditivo.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return

        # Obter tipo de aditivo
        tipo_aditivo = self.tipo_aditivo_widget.get()

        # Validações específicas por tipo
        if tipo_aditivo in ["TEMPO E VALOR", "TEMPO"]:
            if not self.nova_vigencia_entry.get():
                mostrar_mensagem("Erro de Validação", "Nova vigência é obrigatória para este tipo de aditivo.", tipo="erro")
                return

        if tipo_aditivo in ["TEMPO E VALOR", "VALOR"]:
            if not self.nova_remuneracao_entry.get():
                mostrar_mensagem("Erro de Validação", "Nova remuneração é obrigatória para este tipo de aditivo.", tipo="erro")
                return
            if not self.data_inicio_nova_remuneracao_entry.get():
                mostrar_mensagem("Erro de Validação", "Data de início da nova remuneração é obrigatória para este tipo de aditivo.", tipo="erro")
                return

        try:
            # Obter valores do formulário principal
            valores = self.form_aditivo.obter_valores()

            # Mapear tipos para o modelo
            tipo_mapeado = {
                "TEMPO E VALOR": "ambos",
                "TEMPO": "prorrogacao", 
                "VALOR": "reajuste"
            }[tipo_aditivo]

            # Inicializar valores específicos por tipo
            nova_vigencia_final = None
            meses = None
            nova_remuneracao = None
            diferenca_remuneracao = None
            data_inicio_nova_remuneracao = None

            # Obter valores específicos por tipo
            if tipo_aditivo in ["TEMPO E VALOR", "TEMPO"]:
                nova_vigencia_final = self.nova_vigencia_entry.get()
                # Converter formato de data de DD/MM/YYYY para YYYY-MM-DD
                if nova_vigencia_final:
                    from datetime import datetime
                    data_obj = datetime.strptime(nova_vigencia_final, "%d/%m/%Y")
                    nova_vigencia_final = data_obj.strftime("%Y-%m-%d")
                
                meses_str = self.meses_entry.get()
                meses = int(meses_str) if meses_str else 0

            if tipo_aditivo in ["TEMPO E VALOR", "VALOR"]:
                nova_remuneracao = converter_valor_brl_para_float(self.nova_remuneracao_entry.get())
                diferenca_remuneracao = nova_remuneracao - float(self.contrato[18])
                
                # Converter data de início da nova remuneração
                data_inicio_str = self.data_inicio_nova_remuneracao_entry.get()
                if data_inicio_str:
                    from datetime import datetime
                    data_obj = datetime.strptime(data_inicio_str, "%d/%m/%Y")
                    data_inicio_nova_remuneracao = data_obj.strftime("%Y-%m-%d")

            # Converter valores monetários
            valor_complementar = converter_valor_brl_para_float(self.valor_complementar_entry.get())

            # Calcular valor total do aditivo usando a mesma lógica do método calcular_valores_aditivo
            valor_total_aditivo = 0
            remuneracao_atual_valor = float(self.contrato[18])
            vigencia_final_original = self.contrato[15]

            if tipo_aditivo == "TEMPO":
                # Para extensão de tempo, usar a remuneração atual * meses
                valor_total_aditivo = (remuneracao_atual_valor * meses) + valor_complementar
            elif tipo_aditivo == "VALOR":
                # Para reajuste, calcular meses restantes considerando data de início
                meses_restantes = int(self.contrato[16])
                
                if data_inicio_nova_remuneracao:
                    try:
                        from datetime import datetime
                        data_inicio = datetime.strptime(data_inicio_nova_remuneracao, "%Y-%m-%d")
                        data_fim_contrato = datetime.strptime(vigencia_final_original, "%Y-%m-%d")
                        
                        diferenca_anos = data_fim_contrato.year - data_inicio.year
                        diferenca_meses = data_fim_contrato.month - data_inicio.month
                        meses_restantes = diferenca_anos * 12 + diferenca_meses
                        
                        if data_fim_contrato.day < data_inicio.day:
                            meses_restantes -= 1
                            
                        meses_restantes = max(0, meses_restantes)
                    except Exception:
                        pass
                
                valor_total_aditivo = (diferenca_remuneracao * meses_restantes) + valor_complementar
            elif tipo_aditivo == "TEMPO E VALOR":
                # Para ambos, aplicar lógica baseada na data de início da nova remuneração
                if data_inicio_nova_remuneracao:
                    try:
                        from datetime import datetime
                        data_inicio = datetime.strptime(data_inicio_nova_remuneracao, "%Y-%m-%d")
                        data_fim_original = datetime.strptime(vigencia_final_original, "%Y-%m-%d")
                        
                        diferenca_anos = data_fim_original.year - data_inicio.year
                        diferenca_meses = data_fim_original.month - data_inicio.month
                        meses_desde_inicio = diferenca_anos * 12 + diferenca_meses
                        
                        if data_fim_original.day < data_inicio.day:
                            meses_desde_inicio -= 1
                            
                        meses_desde_inicio = max(0, meses_desde_inicio)
                        
                        valor_total_aditivo = (diferenca_remuneracao * meses_desde_inicio) + (nova_remuneracao * meses) + valor_complementar
                    except Exception:
                        valor_total_aditivo = (nova_remuneracao * meses) + valor_complementar
                else:
                    valor_total_aditivo = (nova_remuneracao * meses) + valor_complementar

            # Criar o aditivo
            aditivo_id = adicionar_aditivo(
                id_contrato=self.id_contrato,
                tipo_aditivo=tipo_mapeado,
                oficio=valores["oficio"],
                data_entrada=valores["data_entrada"],
                data_protocolo=valores["data_protocolo"],
                vigencia_final=nova_vigencia_final,
                vigencia_inicial=data_inicio_nova_remuneracao,
                meses=meses,
                valor_aditivo=0,  # Será calculado pela soma dos outros valores
                nova_remuneracao=nova_remuneracao,
                diferenca_remuneracao=diferenca_remuneracao,
                valor_complementar=valor_complementar,
                valor_total_aditivo=valor_total_aditivo,
                responsavel=None,  # Campo removido
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
