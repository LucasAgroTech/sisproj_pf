# Components for ContratoPF views
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from controllers.pessoa_fisica_controller import listar_pessoas, buscar_pessoa_por_id
from controllers.produto_pf_controller import (
    listar_produtos_por_contrato,
    buscar_produto_por_id,
    excluir_produto,
)
from controllers.aditivo_pf_controller import (
    listar_aditivos_por_contrato,
    adicionar_aditivo,
    excluir_aditivo,
)
from controllers.contrato_pf_controller import atualizar_total_contrato
from utils.ui_utils import (
    FormularioBase,
    TabelaBase,
    criar_botao,
    mostrar_mensagem,
    formatar_data,
    formatar_valor_brl,
    validar_numerico,
    converter_valor_brl_para_float,
)


class PessoaFisicaSelector:
    """Componente para seleção de pessoa física"""

    def __init__(self, master, initial_value=None, initial_id=None):
        """
        Args:
            master: widget pai
            initial_value: valor inicial para o combobox (nome da pessoa)
            initial_id: ID inicial da pessoa selecionada
        """
        self.master = master
        self.pessoas_map = {}  # Mapeamento de nomes para IDs

        # Frame para a seleção da pessoa
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.frame, text="Pessoa Física*:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )

        # Frame para combobox e botão de busca
        frame_combo_pessoa = ttk.Frame(self.frame)
        frame_combo_pessoa.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Combobox para seleção da pessoa
        self.pessoa_var = tk.StringVar(value=initial_value if initial_value else "")
        self.pessoa_combobox = ttk.Combobox(
            frame_combo_pessoa, textvariable=self.pessoa_var, width=40
        )
        self.pessoa_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Botão de busca de pessoa
        btn_buscar_pessoa = tk.Button(
            frame_combo_pessoa,
            text="🔍",
            command=self.buscar_pessoa,
            bg="#f0f0f0",
            relief="flat",
            cursor="hand2",
            font=("Segoe UI", 10),
        )
        btn_buscar_pessoa.pack(side=tk.RIGHT, padx=(2, 0))

        # Campo oculto para armazenar o ID da pessoa selecionada
        self.id_pessoa_selecionada = tk.StringVar(value=initial_id if initial_id else "")

        # Vincular evento de seleção do combobox
        self.pessoa_combobox.bind("<<ComboboxSelected>>", self.selecionar_pessoa)

        # Mostrar os dados da pessoa selecionada
        self.frame_info = ttk.Frame(master)
        self.frame_info.pack(fill=tk.X, pady=5)

        ttk.Label(self.frame_info, text="Informações:", width=20, anchor=tk.W).pack(
            side=tk.LEFT
        )
        self.info_pessoa_label = ttk.Label(
            self.frame_info, text="Nenhuma pessoa selecionada", foreground="gray"
        )
        self.info_pessoa_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Carregar pessoas físicas para o combobox
        self.carregar_pessoas()

        # Se tiver valor inicial, atualizar informações
        if initial_id:
            pessoa = buscar_pessoa_por_id(initial_id)
            if pessoa:
                self.atualizar_info_pessoa(pessoa)
                # Garantir que o valor inicial seja definido corretamente
                self.master.after(100, lambda: self.forcar_valor_inicial(initial_value))
                
    def forcar_valor_inicial(self, valor):
        """Força a definição do valor inicial no combobox"""
        if valor:
            self.pessoa_combobox.set(valor)

    def carregar_pessoas(self):
        """Carrega a lista de pessoas físicas para o combobox"""
        try:
            pessoas = listar_pessoas()
            nomes_pessoas = [pessoa[1] for pessoa in pessoas]
            self.pessoa_combobox["values"] = nomes_pessoas

            # Mapeamento de nomes para IDs
            self.pessoas_map = {pessoa[1]: pessoa[0] for pessoa in pessoas}
            
            # Se houver um ID selecionado, garantir que o nome correspondente esteja nas opções
            id_selecionado = self.id_pessoa_selecionada.get()
            if id_selecionado:
                pessoa = buscar_pessoa_por_id(id_selecionado)
                if pessoa and pessoa[1] not in nomes_pessoas:
                    nomes_atualizados = nomes_pessoas + [pessoa[1]]
                    self.pessoa_combobox["values"] = nomes_atualizados
                    self.pessoas_map[pessoa[1]] = pessoa[0]

        except Exception as e:
            print(f"Erro ao carregar pessoas: {e}")

    def buscar_pessoa(self):
        """Abre uma janela para buscar pessoa física"""
        # Criar uma janela de diálogo para a busca
        janela = tk.Toplevel(self.master)
        janela.title("Buscar Pessoa Física")
        janela.transient(self.master)
        janela.grab_set()

        # Centraliza a janela
        largura = 800
        altura = 500
        pos_x = self.master.winfo_rootx() + (self.master.winfo_width() - largura) // 2
        pos_y = self.master.winfo_rooty() + (self.master.winfo_height() - altura) // 2
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

    def get_id(self):
        """Retorna o ID da pessoa selecionada"""
        return self.id_pessoa_selecionada.get()

    def get_nome(self):
        """Retorna o nome da pessoa selecionada"""
        return self.pessoa_var.get()

    def set_state(self, state):
        """Define o estado do componente"""
        self.pessoa_combobox.configure(state=state)


class ProdutosTable:
    """Componente para exibição e gerenciamento de produtos de um contrato"""

    def __init__(self, master, id_contrato, modalidade=None):
        """
        Args:
            master: widget pai
            id_contrato: ID do contrato
            modalidade: modalidade do contrato (para verificar se pode ter produtos)
        """
        self.master = master
        self.id_contrato = id_contrato
        self.modalidade = modalidade

        # Frame para a tabela de produtos
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título e botão para adicionar produto
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            frame_cabecalho,
            text="Produtos do Contrato",
            style="Titulo.TLabel",
        ).pack(side=tk.LEFT)

        # Botão de adicionar produto
        self.btn_adicionar = criar_botao(
            frame_cabecalho,
            "Adicionar Produto",
            self.adicionar_produto,
            "Primario",
            15,
        )
        self.btn_adicionar.pack(side=tk.RIGHT)

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

        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)

        # Frame de botões de ação para produtos
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))

        criar_botao(
            frame_acoes,
            "Visualizar",
            self.visualizar_produto,
            "Primario",
            15,
        ).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(
            frame_acoes,
            "Editar",
            self.editar_produto,
            "Secundario",
            15,
        ).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(
            frame_acoes, "Excluir", self.excluir_produto, "Perigo", 15
        ).pack(side=tk.LEFT)

        # Carregar produtos existentes
        self.carregar_produtos()

    def carregar_produtos(self):
        """Carrega os produtos do contrato na tabela"""
        if not self.id_contrato:
            return

        self.tabela.limpar()

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

            self.tabela.adicionar_linha(valores, str(id_produto))

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
        if self.modalidade == "CLT":
            mostrar_mensagem(
                "Atenção",
                "Contratos CLT não podem ter produtos associados.",
                tipo="aviso",
            )
            return

        # Importar a view de produto
        from views.produto_pf_view import ProdutoPFForm

        # Criar uma janela de diálogo para o formulário de produto
        dialog = tk.Toplevel(self.master)
        dialog.title("Adicionar Produto")
        dialog.geometry("800x600")
        dialog.transient(self.master)
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
        id_selecao = self.tabela.obter_selecao()
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

    def editar_produto(self):
        """Edita um produto existente"""
        id_selecao = self.tabela.obter_selecao()
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
        dialog = tk.Toplevel(self.master)
        dialog.title("Editar Produto")
        dialog.geometry("800x600")
        dialog.transient(self.master)
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
                self.carregar_produtos()
            except Exception as e:
                mostrar_mensagem("Erro", f"Erro ao excluir produto: {e}", tipo="erro")


class AditivosTable:
    """Componente para exibição e gerenciamento de aditivos de um contrato"""

    def __init__(self, master, id_contrato, callback_aditivo_added=None):
        """
        Args:
            master: widget pai
            id_contrato: ID do contrato
            callback_aditivo_added: função a ser chamada quando um aditivo for adicionado
        """
        self.master = master
        self.id_contrato = id_contrato
        self.callback_aditivo_added = callback_aditivo_added

        # Frame para a tabela de aditivos
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título e botão para adicionar aditivo
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            frame_cabecalho,
            text="Aditivos do Contrato",
            style="Titulo.TLabel",
        ).pack(side=tk.LEFT)

        # Botão de adicionar aditivo
        self.btn_adicionar = criar_botao(
            frame_cabecalho,
            "Adicionar Aditivo",
            self.adicionar_aditivo,
            "Primario",
            15,
        )
        self.btn_adicionar.pack(side=tk.RIGHT)

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

        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)

        # Frame de botões de ação para aditivos
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))

        criar_botao(
            frame_acoes,
            "Visualizar",
            self.visualizar_aditivo,
            "Primario",
            15,
        ).pack(side=tk.LEFT, padx=(0, 5))
        criar_botao(
            frame_acoes, "Excluir", self.excluir_aditivo, "Perigo", 15
        ).pack(side=tk.LEFT)

        # Carregar aditivos existentes
        self.carregar_aditivos()

    def carregar_aditivos(self):
        """Carrega os aditivos do contrato na tabela"""
        if not self.id_contrato:
            return

        self.tabela.limpar()

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
                "prorrogacao": "TEMPO",
                "reajuste": "VALOR", 
                "ambos": "TEMPO E VALOR",
                "tempo": "TEMPO",
                "valor": "VALOR",
                "tempo e valor": "TEMPO E VALOR",
                "TEMPO": "TEMPO",
                "VALOR": "VALOR",
                "TEMPO E VALOR": "TEMPO E VALOR",
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

            self.tabela.adicionar_linha(valores, str(id_aditivo))

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
        from controllers.contrato_pf_controller import buscar_contrato_por_id
        contrato = buscar_contrato_por_id(self.id_contrato)
        if contrato and contrato[11] == "CLT":
            mostrar_mensagem(
                "Atenção",
                "Contratos CLT não podem ter aditivos associados.",
                tipo="aviso",
            )
            return

        # Importar a view de aditivo
        from views.contrato_pf.aditivo_form import AditivoPFForm

        # Criar uma janela de diálogo para o formulário de aditivo
        dialog = tk.Toplevel(self.master)
        dialog.title("Adicionar Aditivo")
        dialog.geometry("800x600")
        dialog.transient(self.master)
        dialog.grab_set()

        # Função de callback para quando o aditivo for salvo
        def aditivo_salvo(aditivo_data):
            dialog.destroy()
            self.carregar_aditivos()
            
            # Chamar o callback se existir
            if self.callback_aditivo_added:
                self.callback_aditivo_added(aditivo_data)

        # Função de callback para quando o formulário for cancelado
        def aditivo_cancelado():
            dialog.destroy()

        # Criar o formulário de aditivo
        form_aditivo = AditivoPFForm(
            dialog,
            id_contrato=self.id_contrato,
            callback_salvar=aditivo_salvo,
            callback_cancelar=aditivo_cancelado,
        )
        form_aditivo.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def visualizar_aditivo(self):
        """Visualiza os detalhes de um aditivo (somente leitura)"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione um aditivo para visualizar.", tipo="aviso"
            )
            return

        # TODO: Implementar visualização de aditivo
        mostrar_mensagem(
            "Visualizar Aditivo", f"Visualizando aditivo ID: {id_selecao}", tipo="info"
        )

    def excluir_aditivo(self):
        """Exclui o aditivo selecionado"""
        id_selecao = self.tabela.obter_selecao()
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
                
                # Atualizar o total do contrato após exclusão do aditivo
                atualizar_total_contrato(self.id_contrato)
                
                mostrar_mensagem(
                    "Sucesso", "Aditivo excluído com sucesso!", tipo="sucesso"
                )
                self.carregar_aditivos()

                # Chamar o callback se existir
                if self.callback_aditivo_added:
                    self.callback_aditivo_added(None)  # Passar None para indicar exclusão

            except ValueError as e:
                mostrar_mensagem("Erro", str(e), tipo="erro")
