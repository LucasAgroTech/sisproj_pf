# Produto Pf View.Py
import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime

from controllers.produto_pf_controller import (
    adicionar_produto,
    listar_produtos,
    buscar_produto_por_id,
    listar_produtos_por_contrato,
    editar_produto,
    excluir_produto,
)
from controllers.contrato_pf_controller import listar_contratos, buscar_contrato_por_id
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


class ProdutoPFForm(FormularioBase):
    """Formulário para cadastro e edição de produtos de contratos PF"""

    def __init__(
        self, master, callback_salvar, callback_cancelar, produto=None, id_contrato=None
    ):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            produto: dados do produto para edição (opcional)
            id_contrato: ID do contrato para pré-selecionar (opcional)
        """
        super().__init__(
            master, "Cadastro de Produto" if not produto else "Edição de Produto"
        )

        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.produto = produto
        self.id_produto = produto[0] if produto else None
        self.modo_edicao = produto is not None

        # Contrato associado
        self.id_contrato_selecionado = None

        # Frame para seleção do contrato
        frame_contrato = ttk.Frame(self)
        frame_contrato.pack(fill=tk.X, pady=5)

        ttk.Label(frame_contrato, text="Contrato*:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )

        # Frame para combobox e botão de busca
        frame_combo_contrato = ttk.Frame(frame_contrato)
        frame_combo_contrato.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Combobox para seleção do contrato
        self.contrato_var = tk.StringVar()
        self.contrato_combobox = ttk.Combobox(
            frame_combo_contrato, textvariable=self.contrato_var, width=40
        )
        self.contrato_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botão de busca de contrato
        btn_buscar_contrato = tk.Button(
            frame_combo_contrato,
            text="🔍",
            command=self.buscar_contrato,
            bg=Cores.BACKGROUND_CLARO,
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
        )
        btn_buscar_contrato.pack(side=tk.RIGHT, padx=(2, 0))

        # Carregar contratos para o combobox
        self.carregar_contratos()

        # Vincular evento de seleção do combobox
        self.contrato_combobox.bind("<<ComboboxSelected>>", self.selecionar_contrato)

        # Mostrar os dados do contrato selecionado
        frame_info_contrato = ttk.Frame(self)
        frame_info_contrato.pack(fill=tk.X, pady=5)

        ttk.Label(frame_info_contrato, text="Informações:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )
        self.info_contrato_label = ttk.Label(
            frame_info_contrato, text="Nenhum contrato selecionado", foreground="gray"
        )
        self.info_contrato_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Se for edição, selecionar o contrato do produto
        if self.modo_edicao and produto:
            id_contrato_produto = produto[1]  # ID do contrato
            contrato = buscar_contrato_por_id(id_contrato_produto)
            if contrato:
                self.id_contrato_selecionado = id_contrato_produto
                self.contrato_var.set(
                    f"{contrato[13]} - {contrato[-1]}"
                )  # Número do contrato e nome da pessoa
                self.atualizar_info_contrato(contrato)
        elif id_contrato:
            # Se foi fornecido um ID de contrato específico
            contrato = buscar_contrato_por_id(id_contrato)
            if contrato:
                self.id_contrato_selecionado = id_contrato
                self.contrato_var.set(
                    f"{contrato[13]} - {contrato[-1]}"
                )  # Número do contrato e nome da pessoa
                self.atualizar_info_contrato(contrato)

        # Separador
        ttk.Separator(self).pack(fill=tk.X, pady=10)

        # Campos do produto
        self.adicionar_campo(
            "numero",
            "Número do Produto",
            padrao=produto[2] if produto else "",
            required=True,
        )

        self.adicionar_campo(
            "data_programada",
            "Data Programada",
            tipo="data",
            padrao=produto[3] if produto else "",
            required=True,
        )
        # Configurar formatação para data programada
        data_programada_widget = self.campos["data_programada"]["widget"]
        data_programada_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_programada_widget, e)
        )

        self.adicionar_campo(
            "instrumento", "Instrumento", padrao=produto[4] if produto else ""
        )

        self.adicionar_campo(
            "data_entrega",
            "Data de Entrega",
            tipo="data",
            padrao=produto[5] if produto else "",
        )
        # Configurar formatação para data de entrega
        data_entrega_widget = self.campos["data_entrega"]["widget"]
        data_entrega_widget.bind(
            "<KeyRelease>", lambda e: formatar_data(data_entrega_widget, e)
        )

        # Status do produto
        status_opcoes = ["programado", "em_execucao", "entregue", "cancelado"]
        status_map = {
            "programado": "Programado",
            "em_execucao": "Em Execução",
            "entregue": "Entregue",
            "cancelado": "Cancelado",
        }

        status_exibicao = [status_map.get(status, status) for status in status_opcoes]

        # Status padrão
        status_padrao = (
            status_map.get(produto[6], "Programado") if produto else "Programado"
        )

        self.adicionar_campo(
            "status",
            "Status",
            tipo="opcoes",
            opcoes=status_exibicao,
            padrao=status_padrao,
            required=True,
        )

        # Mapear status de exibição de volta para valores reais
        self.status_map_reverso = {
            exibicao: real for real, exibicao in status_map.items()
        }

        self.adicionar_campo(
            "titulo", "Título", padrao=produto[7] if produto else "", required=True
        )

        self.adicionar_campo(
            "valor",
            "Valor",
            tipo="numero",
            padrao=produto[8] if produto else "",
            required=True,
        )
        # Configurar formatação para valor
        valor_widget = self.campos["valor"]["widget"]
        valor_widget.bind("<KeyRelease>", lambda e: formatar_valor_brl(valor_widget, e))

        # Campo de observações/notas (novo campo adicional)
        self.adicionar_campo(
            "observacoes",
            "Observações",
            tipo="texto_longo",
            padrao=produto[9] if produto and len(produto) > 9 else "",
        )

        # Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=20)

        criar_botao(frame_botoes, "Cancelar", self.cancelar, "Secundario", 15).pack(
            side=tk.RIGHT, padx=5
        )
        criar_botao(frame_botoes, "Salvar", self.salvar, "Primario", 15).pack(
            side=tk.RIGHT
        )

    def carregar_contratos(self):
        """Carrega a lista de contratos para o combobox"""
        try:
            contratos = listar_contratos()

            # Filtrar apenas contratos de modalidade elegível para produtos
            contratos_filtrados = []
            for contrato in contratos:
                modalidade = contrato[11]
                status_contrato = contrato[17]
                # Adicionar verificação de status ativo
                if modalidade in ["BOLSA", "PRODUTO", "RPA"] and status_contrato in [
                    "vigente",
                    "em_tramitacao",
                ]:
                    contratos_filtrados.append(contrato)

            # Formatar para exibição
            contratos_exibicao = []
            for contrato in contratos_filtrados:
                numero_contrato = contrato[13]
                nome_pessoa = contrato[-1]
                contratos_exibicao.append(f"{numero_contrato} - {nome_pessoa}")

            self.contrato_combobox["values"] = contratos_exibicao

            # Mapeamento para recuperar o ID
            self.contratos_map = {}
            for i, contrato in enumerate(contratos_filtrados):
                self.contratos_map[contratos_exibicao[i]] = contrato[0]

        except Exception as e:
            print(f"Erro ao carregar contratos: {e}")
            mostrar_mensagem("Erro", f"Erro ao carregar contratos: {e}", tipo="erro")

    def buscar_contrato(self):
        """Abre uma janela para buscar contrato"""
        # Criar uma janela de diálogo para a busca
        janela = tk.Toplevel(self)
        janela.title("Buscar Contrato")
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
        colunas = [
            "id",
            "nome_completo",
            "modalidade",
            "numero_contrato",
            "status_contrato",
        ]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome",
            "modalidade": "Modalidade",
            "numero_contrato": "Número do Contrato",
            "status_contrato": "Status",
        }

        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True, pady=10)

        # Função para carregar dados na tabela
        def carregar_dados(filtro=None):
            tabela.limpar()

            try:
                contratos = listar_contratos()

                for contrato in contratos:
                    # Filtrar apenas contratos de modalidade elegível para produtos
                    modalidade = contrato[11]
                    if modalidade not in ["BOLSA", "PRODUTO", "RPA"]:
                        continue

                    # Se tiver filtro, verifica se contrato contém o texto do filtro
                    if filtro:
                        texto_filtro = filtro.lower()
                        texto_contrato = " ".join(
                            str(campo).lower() for campo in contrato if campo
                        )
                        if texto_filtro not in texto_contrato:
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

                    # Nome da pessoa física
                    nome_pessoa = contrato[-1]

                    valores = {
                        "id": contrato[0],
                        "nome_completo": nome_pessoa,
                        "modalidade": contrato[11],
                        "numero_contrato": contrato[13],
                        "status_contrato": status_exibicao,
                    }
                    tabela.adicionar_linha(valores, str(contrato[0]))
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
                mostrar_mensagem("Erro", f"Erro ao carregar dados: {e}", tipo="erro")

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

        # Função para selecionar o contrato e fechar a janela
        def selecionar():
            id_selecao = tabela.obter_selecao()
            if id_selecao:
                # Buscar o contrato selecionado
                contrato = buscar_contrato_por_id(id_selecao)
                if contrato:
                    # Atualizar o combobox e o id selecionado
                    self.id_contrato_selecionado = contrato[0]
                    self.contrato_var.set(f"{contrato[13]} - {contrato[-1]}")
                    self.atualizar_info_contrato(contrato)
                    janela.destroy()
            else:
                mostrar_mensagem("Atenção", "Selecione um contrato.", tipo="aviso")

        # Frame de botões
        frame_botoes = ttk.Frame(frame)
        frame_botoes.pack(fill=tk.X, pady=10)

        criar_botao(frame_botoes, "Cancelar", janela.destroy, "Secundario", 15).pack(
            side=tk.RIGHT, padx=5
        )
        criar_botao(frame_botoes, "Selecionar", selecionar, "Primario", 15).pack(
            side=tk.RIGHT
        )

    def selecionar_contrato(self, event=None):
        """Callback quando um contrato é selecionado no combobox"""
        contrato_exibicao = self.contrato_var.get()

        if contrato_exibicao in self.contratos_map:
            id_contrato = self.contratos_map[contrato_exibicao]
            self.id_contrato_selecionado = id_contrato

            # Buscar dados completos do contrato
            contrato = buscar_contrato_por_id(id_contrato)
            if contrato:
                self.atualizar_info_contrato(contrato)

    def atualizar_info_contrato(self, contrato):
        """Atualiza o label de informações do contrato"""
        if not contrato:
            self.info_contrato_label.config(
                text="Nenhum contrato selecionado", foreground="gray"
            )
            return

        modalidade = contrato[11]

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

        info_text = f"Modalidade: {modalidade} | Status: {status_exibicao} | Vigência: {contrato[14]} a {contrato[15]}"
        self.info_contrato_label.config(text=info_text, foreground="black")

    def validar_campos_customizados(self):
        """Validações customizadas específicas do formulário de produtos"""
        erros = []

        # Validar se data programada não é anterior a hoje
        data_programada = self.campos["data_programada"]["widget"].get().strip()
        if data_programada:
            try:
                data_prog = datetime.strptime(data_programada, "%d/%m/%Y").date()
                if data_prog < datetime.now().date():
                    erros.append("Data programada não pode ser anterior à data atual.")
            except ValueError:
                erros.append("Data programada deve estar no formato DD/MM/AAAA.")

        # Validar se data de entrega não é anterior à data programada
        data_entrega = self.campos["data_entrega"]["widget"].get().strip()
        if data_entrega and data_programada:
            try:
                data_prog = datetime.strptime(data_programada, "%d/%m/%Y").date()
                data_ent = datetime.strptime(data_entrega, "%d/%m/%Y").date()
                if data_ent < data_prog:
                    erros.append(
                        "Data de entrega não pode ser anterior à data programada."
                    )
            except ValueError:
                erros.append("Data de entrega deve estar no formato DD/MM/AAAA.")

        # Validar valor mínimo
        valor_str = self.campos["valor"]["widget"].get().strip()
        if valor_str:
            try:
                valor = converter_valor_brl_para_float(valor_str)
                if valor <= 0:
                    erros.append("Valor deve ser maior que zero.")
            except ValueError:
                erros.append("Valor deve ser um número válido.")

        return erros

    def salvar(self):
        """Salva os dados do formulário"""
        # Validar o formulário
        valido, mensagem = self.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return

        # Validações customizadas
        erros_customizados = self.validar_campos_customizados()
        if erros_customizados:
            mostrar_mensagem(
                "Erro de Validação", "\n".join(erros_customizados), tipo="erro"
            )
            return

        # Verificar se um contrato foi selecionado
        if not self.id_contrato_selecionado:
            mostrar_mensagem("Erro de Validação", "Selecione um contrato.", tipo="erro")
            return

        try:
            # Obter valores dos campos
            valores = self.obter_valores()

            # Converter status de exibição para valor real
            status_exibicao = valores["status"]
            status_real = self.status_map_reverso.get(status_exibicao, "programado")

            # Converter valor para float
            valor = converter_valor_brl_para_float(valores["valor"])

            # Obter observações
            observacoes = valores.get("observacoes", "")

            if self.modo_edicao:  # Edição
                editar_produto(
                    self.id_produto,
                    valores["numero"],
                    valores["data_programada"],
                    valores["instrumento"],
                    valores["data_entrega"],
                    status_real,
                    valores["titulo"],
                    valor,
                    observacoes,
                )
                mostrar_mensagem(
                    "Sucesso", "Produto atualizado com sucesso!", tipo="sucesso"
                )
            else:  # Novo cadastro
                adicionar_produto(
                    self.id_contrato_selecionado,
                    valores["numero"],
                    valores["data_programada"],
                    valores["instrumento"],
                    valores["data_entrega"],
                    status_real,
                    valores["titulo"],
                    valor,
                    observacoes,
                )
                mostrar_mensagem(
                    "Sucesso", "Produto cadastrado com sucesso!", tipo="sucesso"
                )

            self.callback_salvar()

        except ValueError as e:
            mostrar_mensagem("Erro", str(e), tipo="erro")
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro inesperado: {e}", tipo="erro")

    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


class ProdutoPFView:
    """Tela principal de listagem e gestão de produtos de contratos PF"""

    def __init__(self, master, id_contrato=None):
        """
        Args:
            master: widget pai
            id_contrato: ID do contrato para filtrar produtos (opcional)
        """
        self.master = master
        self.id_contrato = id_contrato

        # Verifica se o master é uma janela principal para definir o título
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            titulo = "Gestão de Produtos"
            if id_contrato:
                contrato = buscar_contrato_por_id(id_contrato)
                if contrato:
                    titulo += f" - Contrato {contrato[13]}"
            self.master.title(titulo)

        # Configura estilos
        Estilos.configurar()

        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))

        titulo_label = "Gestão de Produtos"
        if id_contrato:
            contrato = buscar_contrato_por_id(id_contrato)
            if contrato:
                titulo_label += f" - Contrato {contrato[13]}"

        ttk.Label(frame_cabecalho, text=titulo_label, style="Titulo.TLabel").pack(
            side=tk.LEFT
        )

        # Botão de adicionar produto (diferenciado se for filtrado por contrato)
        if id_contrato:
            criar_botao(
                frame_cabecalho,
                "Novo Produto para este Contrato",
                lambda: self.adicionar(id_contrato),
                "Primario",
                20,
            ).pack(side=tk.RIGHT)
        else:
            criar_botao(
                frame_cabecalho, "Novo Produto", self.adicionar, "Primario", 15
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

        if id_contrato:
            criar_botao(
                frame_pesquisa, "Ver Todos os Produtos", self.ver_todos, "Primario", 15
            ).pack(side=tk.RIGHT)

        # Frame de filtros
        frame_filtros = ttk.Frame(self.frame)
        frame_filtros.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_filtros, text="Filtrar por:").pack(side=tk.LEFT, padx=(0, 5))

        # Filtro por status
        ttk.Label(frame_filtros, text="Status:").pack(side=tk.LEFT, padx=(10, 5))
        self.filtro_status = ttk.Combobox(
            frame_filtros,
            values=["Todos", "Programado", "Em Execução", "Entregue", "Cancelado"],
            width=15,
        )
        self.filtro_status.current(0)
        self.filtro_status.pack(side=tk.LEFT, padx=(0, 10))

        # Filtro por data
        ttk.Label(frame_filtros, text="Data de:").pack(side=tk.LEFT, padx=(10, 5))
        self.data_inicio_entry = ttk.Entry(frame_filtros, width=12)
        self.data_inicio_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.data_inicio_entry.bind(
            "<KeyRelease>", lambda e: formatar_data(self.data_inicio_entry, e)
        )

        ttk.Label(frame_filtros, text="até:").pack(side=tk.LEFT, padx=(5, 5))
        self.data_fim_entry = ttk.Entry(frame_filtros, width=12)
        self.data_fim_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.data_fim_entry.bind(
            "<KeyRelease>", lambda e: formatar_data(self.data_fim_entry, e)
        )

        # Botão para aplicar filtros
        criar_botao(
            frame_filtros, "Aplicar Filtros", self.aplicar_filtros, "Primario", 12
        ).pack(side=tk.LEFT)

        # Tabela de produtos
        colunas = [
            "id",
            "id_contrato",
            "numero",
            "titulo",
            "data_programada",
            "data_entrega",
            "status",
            "valor",
        ]
        titulos = {
            "id": "ID",
            "id_contrato": "ID Contrato",
            "numero": "Número",
            "titulo": "Título",
            "data_programada": "Data Programada",
            "data_entrega": "Data Entrega",
            "status": "Status",
            "valor": "Valor (R$)",
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

        # Botões adicionais
        criar_botao(
            frame_acoes, "Relatório", self.gerar_relatorio, "Secundario", 15
        ).pack(side=tk.RIGHT, padx=(5, 0))
        criar_botao(
            frame_acoes, "Exportar", self.exportar_dados, "Secundario", 15
        ).pack(side=tk.RIGHT)

        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)

        # Carrega os dados
        self.carregar_dados()

    def carregar_dados(
        self, filtro=None, filtro_status=None, data_inicio=None, data_fim=None
    ):
        """Carrega os dados dos produtos na tabela"""
        self.tabela.limpar()

        try:
            # Carregar produtos (filtrados por contrato se especificado)
            if self.id_contrato:
                produtos = listar_produtos_por_contrato(self.id_contrato)
            else:
                produtos = listar_produtos()

            for produto in produtos:
                # Aplicar filtros de texto
                if filtro:
                    texto_filtro = filtro.lower()
                    texto_produto = " ".join(
                        str(campo).lower() for campo in produto if campo
                    )
                    if texto_filtro not in texto_produto:
                        continue

                # Status para exibição
                status_map = {
                    "programado": "Programado",
                    "em_execucao": "Em Execução",
                    "entregue": "Entregue",
                    "cancelado": "Cancelado",
                }
                status_exibicao = status_map.get(produto[5], produto[5])

                # Filtrar por status
                if filtro_status and filtro_status != "Todos":
                    if status_exibicao != filtro_status:
                        continue

                # Filtrar por data
                if data_inicio or data_fim:
                    try:
                        data_produto = (
                            datetime.strptime(produto[3], "%Y-%m-%d").date()
                            if produto[3]
                            else None
                        )
                        if data_produto:
                            if data_inicio:
                                data_ini = datetime.strptime(
                                    data_inicio, "%d/%m/%Y"
                                ).date()
                                if data_produto < data_ini:
                                    continue
                            if data_fim:
                                data_final = datetime.strptime(
                                    data_fim, "%d/%m/%Y"
                                ).date()
                                if data_produto > data_final:
                                    continue
                    except ValueError:
                        # Se houver erro na conversão de data, ignora o filtro de data
                        pass

                # Formatação de valor monetário
                try:
                    valor = float(produto[7]) if produto[7] else 0.0
                    valor_formatado = (
                        f"R$ {valor:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )
                except (ValueError, TypeError):
                    valor_formatado = "R$ 0,00"

                # Formatação de data
                data_programada_formatada = produto[3]
                if produto[3]:
                    try:
                        data_programada_formatada = datetime.strptime(
                            produto[3], "%Y-%m-%d"
                        ).strftime("%d/%m/%Y")
                    except ValueError:
                        pass

                data_entrega_formatada = produto[4] or "-"
                if produto[4]:
                    try:
                        data_entrega_formatada = datetime.strptime(
                            produto[4], "%Y-%m-%d"
                        ).strftime("%d/%m/%Y")
                    except ValueError:
                        pass

                valores = {
                    "id": produto[0],
                    "id_contrato": produto[1],
                    "numero": produto[2],
                    "titulo": produto[6],
                    "data_programada": data_programada_formatada,
                    "data_entrega": data_entrega_formatada,
                    "status": status_exibicao,
                    "valor": valor_formatado,
                }
                self.tabela.adicionar_linha(valores, str(produto[0]))
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            mostrar_mensagem("Erro", f"Erro ao carregar dados: {e}", tipo="erro")

    def pesquisar(self):
        """Filtra os produtos conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        status = (
            self.filtro_status.get() if self.filtro_status.get() != "Todos" else None
        )
        data_inicio = self.data_inicio_entry.get().strip() or None
        data_fim = self.data_fim_entry.get().strip() or None

        self.carregar_dados(texto, status, data_inicio, data_fim)

    def limpar_pesquisa(self):
        """Limpa os campos de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.filtro_status.current(0)
        self.data_inicio_entry.delete(0, tk.END)
        self.data_fim_entry.delete(0, tk.END)
        self.carregar_dados()

    def aplicar_filtros(self):
        """Aplica os filtros selecionados"""
        texto = self.pesquisa_entry.get().strip()
        status = (
            self.filtro_status.get() if self.filtro_status.get() != "Todos" else None
        )
        data_inicio = self.data_inicio_entry.get().strip() or None
        data_fim = self.data_fim_entry.get().strip() or None

        self.carregar_dados(texto, status, data_inicio, data_fim)

    def ver_todos(self):
        """Remove o filtro por contrato"""
        # Cria uma nova janela com todos os produtos
        janela = tk.Toplevel(self.master)
        janela.title("Todos os Produtos")
        janela.geometry("1200x700")
        janela.transient(self.master)

        # Instancia a view de produtos sem filtro
        ProdutoPFView(janela)

    def adicionar(self, id_contrato=None):
        """Abre o formulário para adicionar um novo produto"""
        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário
        self.formulario = ProdutoPFForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
            id_contrato=id_contrato or self.id_contrato,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def visualizar(self):
        """Abre o formulário para visualizar o produto selecionado (somente leitura)"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um produto para visualizar.", tipo="aviso"
            )
            return

        # Busca o produto selecionado
        produto = buscar_produto_por_id(id_selecao)
        if not produto:
            mostrar_mensagem("Erro", "Produto não encontrado.", tipo="erro")
            return

        # Cria uma janela modal para visualização
        janela = tk.Toplevel(self.master)
        janela.title("Visualizar Produto")
        janela.transient(self.master)
        janela.grab_set()

        # Centraliza a janela
        largura = 650
        altura = 600
        pos_x = self.master.winfo_rootx() + (self.master.winfo_width() - largura) // 2
        pos_y = self.master.winfo_rooty() + (self.master.winfo_height() - altura) // 2
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

    def editar(self):
        """Abre o formulário para editar o produto selecionado"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um produto para editar.", tipo="aviso"
            )
            return

        # Busca o produto selecionado
        produto = buscar_produto_por_id(id_selecao)
        if not produto:
            mostrar_mensagem("Erro", "Produto não encontrado.", tipo="erro")
            return

        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário de edição
        self.formulario = ProdutoPFForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
            produto=produto,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def excluir(self):
        """Exclui o produto selecionado"""
        id_selecao = self.tabela.obter_selecao()
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
                self.carregar_dados()
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao excluir produto: {e}", tipo="erro")

    def gerar_relatorio(self):
        """Gera relatório dos produtos"""
        try:
            from utils.relatorio_utils import gerar_relatorio_produtos

            # Obter dados filtrados
            texto = self.pesquisa_entry.get().strip()
            status = (
                self.filtro_status.get()
                if self.filtro_status.get() != "Todos"
                else None
            )
            data_inicio = self.data_inicio_entry.get().strip() or None
            data_fim = self.data_fim_entry.get().strip() or None

            # Gerar relatório
            if self.id_contrato:
                produtos = listar_produtos_por_contrato(self.id_contrato)
            else:
                produtos = listar_produtos()

            gerar_relatorio_produtos(produtos, self.id_contrato)
            mostrar_mensagem("Sucesso", "Relatório gerado com sucesso!", tipo="sucesso")

        except ImportError:
            mostrar_mensagem(
                "Erro", "Módulo de relatórios não encontrado.", tipo="erro"
            )
        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao gerar relatório: {e}", tipo="erro")

    def exportar_dados(self):
        """Exporta os dados para CSV"""
        try:
            from tkinter import filedialog
            import csv

            # Solicitar local para salvar
            arquivo = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar exportação como...",
            )

            if arquivo:
                # Obter dados da tabela
                if self.id_contrato:
                    produtos = listar_produtos_por_contrato(self.id_contrato)
                else:
                    produtos = listar_produtos()

                # Escrever CSV
                with open(arquivo, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)

                    # Cabeçalho
                    writer.writerow(
                        [
                            "ID",
                            "ID Contrato",
                            "Número",
                            "Data Programada",
                            "Instrumento",
                            "Data Entrega",
                            "Status",
                            "Título",
                            "Valor",
                        ]
                    )

                    # Dados
                    for produto in produtos:
                        writer.writerow(produto[:9])  # Primeiros 9 campos

                mostrar_mensagem(
                    "Sucesso", f"Dados exportados para {arquivo}", tipo="sucesso"
                )

        except Exception as e:
            mostrar_mensagem("Erro", f"Erro ao exportar dados: {e}", tipo="erro")

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


# Função utilitária para iniciar a aplicação
def iniciar_aplicacao_produtos(master=None, id_contrato=None):
    """Inicia a aplicação de gestão de produtos"""
    if master is None:
        root = tk.Tk()
        root.geometry("1200x800")
        root.state("zoomed")  # Maximiza a janela no Windows
        app = ProdutoPFView(root, id_contrato)
        root.mainloop()
    else:
        return ProdutoPFView(master, id_contrato)


if __name__ == "__main__":
    iniciar_aplicacao_produtos()
