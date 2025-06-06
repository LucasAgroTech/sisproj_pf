# Pessoa Fisica View.Py
import tkinter as tk
from tkinter import ttk
import re
from controllers.pessoa_fisica_controller import (
    adicionar_pessoa_fisica,
    listar_pessoas,
    buscar_pessoa_por_id,
    buscar_pessoas,
    editar_pessoa_fisica,
    excluir_pessoa_fisica,
)
from controllers.contrato_pf_controller import listar_contratos_por_pessoa
from utils.ui_utils import (
    FormularioBase,
    TabelaBase,
    criar_botao,
    mostrar_mensagem,
    Estilos,
    formatar_cpf,
    formatar_telefone,
    validar_numerico,
)


class PessoaFisicaForm(FormularioBase):
    """Formulário para cadastro e edição de pessoas físicas"""

    def __init__(self, master, callback_salvar, callback_cancelar, pessoa=None):
        """
        Args:
            master: widget pai
            callback_salvar: função a ser chamada quando o formulário for salvo
            callback_cancelar: função a ser chamada quando o formulário for cancelado
            pessoa: dados da pessoa para edição (opcional)
        """
        super().__init__(
            master,
            "Cadastro de Pessoa Física" if not pessoa else "Edição de Pessoa Física",
        )

        self.callback_salvar = callback_salvar
        self.callback_cancelar = callback_cancelar
        self.pessoa = pessoa
        self.id_pessoa = pessoa[0] if pessoa else None

        # Campos do formulário
        self.adicionar_campo(
            "nome_completo",
            "Nome Completo",
            padrao=pessoa[1] if pessoa else "",
            required=True,
        )

        self.adicionar_campo("cpf", "CPF", padrao=pessoa[2] if pessoa else "")
        # Formatação para CPF
        cpf_widget = self.campos["cpf"]["widget"]
        cpf_widget.bind("<KeyRelease>", lambda e: formatar_cpf(cpf_widget, e))
        cpf_widget.bind("<KeyPress>", validar_numerico)

        self.adicionar_campo("email", "E-mail", padrao=pessoa[3] if pessoa else "")

        self.adicionar_campo("telefone", "Telefone", padrao=pessoa[4] if pessoa else "")
        # Formatação para telefone
        telefone_widget = self.campos["telefone"]["widget"]
        telefone_widget.bind(
            "<KeyRelease>", lambda e: formatar_telefone(telefone_widget, e)
        )
        telefone_widget.bind("<KeyPress>", validar_numerico)

        # Botões de ação
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill=tk.X, pady=20)

        criar_botao(frame_botoes, "Cancelar", self.cancelar, "Secundario", 15).pack(
            side=tk.RIGHT, padx=5
        )
        criar_botao(frame_botoes, "Salvar", self.salvar, "Primario", 15).pack(
            side=tk.RIGHT
        )

    def salvar(self):
        """Salva os dados do formulário"""
        # Validar o formulário
        valido, mensagem = self.validar()
        if not valido:
            mostrar_mensagem("Erro de Validação", mensagem, tipo="erro")
            return

        # Obter valores dos campos
        valores = self.obter_valores()

        try:
            if self.pessoa:  # Edição
                editar_pessoa_fisica(
                    self.id_pessoa,
                    valores["nome_completo"],
                    valores["cpf"],
                    valores["email"],
                    valores["telefone"],
                )
                mostrar_mensagem(
                    "Sucesso", "Pessoa física atualizada com sucesso!", tipo="sucesso"
                )
            else:  # Novo cadastro
                adicionar_pessoa_fisica(
                    valores["nome_completo"],
                    valores["cpf"],
                    valores["email"],
                    valores["telefone"],
                )
                mostrar_mensagem(
                    "Sucesso", "Pessoa física cadastrada com sucesso!", tipo="sucesso"
                )

            self.callback_salvar()

        except ValueError as e:
            mostrar_mensagem("Erro", str(e), tipo="erro")

    def cancelar(self):
        """Cancela a operação e fecha o formulário"""
        self.callback_cancelar()


class PessoaFisicaView:
    """Tela principal de listagem e gestão de pessoas físicas"""

    def __init__(self, master):
        self.master = master

        # Verifica se o master é uma janela principal para definir o título
        if isinstance(master, (tk.Tk, tk.Toplevel)):
            self.master.title("Gestão de Pessoas Físicas")

        # Configura estilos
        Estilos.configurar()

        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame de cabeçalho
        frame_cabecalho = ttk.Frame(self.frame)
        frame_cabecalho.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            frame_cabecalho, text="Gestão de Pessoas Físicas", style="Titulo.TLabel"
        ).pack(side=tk.LEFT)
        criar_botao(
            frame_cabecalho, "Nova Pessoa", self.adicionar, "Primario", 15
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

        # Tabela de pessoas
        colunas = ["id", "nome_completo", "cpf", "email", "telefone", "data_cadastro"]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome Completo",
            "cpf": "CPF",
            "email": "E-mail",
            "telefone": "Telefone",
            "data_cadastro": "Data de Cadastro",
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
            frame_acoes, "Ver Contratos", self.ver_contratos, "Primario", 15
        ).pack(side=tk.LEFT)

        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)

        # Carrega os dados
        self.carregar_dados()

    def carregar_dados(self, filtro=None):
        """Carrega os dados das pessoas na tabela"""
        self.tabela.limpar()

        if filtro:
            pessoas = buscar_pessoas(filtro)
        else:
            pessoas = listar_pessoas()

        for pessoa in pessoas:
            valores = {
                "id": pessoa[0],
                "nome_completo": pessoa[1],
                "cpf": pessoa[2] or "",
                "email": pessoa[3] or "",
                "telefone": pessoa[4] or "",
                "data_cadastro": pessoa[5] or "",
            }
            self.tabela.adicionar_linha(valores, str(pessoa[0]))

    def pesquisar(self):
        """Filtra as pessoas conforme o texto de pesquisa"""
        texto = self.pesquisa_entry.get().strip()
        if texto:
            self.carregar_dados(texto)
        else:
            self.carregar_dados()

    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e recarrega todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.carregar_dados()

    def adicionar(self):
        """Abre o formulário para adicionar uma nova pessoa"""
        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário
        self.formulario = PessoaFisicaForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def visualizar(self):
        """Abre o formulário para visualizar a pessoa selecionada (somente leitura)"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione uma pessoa para visualizar.", tipo="aviso"
            )
            return

        # Busca a pessoa selecionada
        pessoa = buscar_pessoa_por_id(id_selecao)
        if not pessoa:
            mostrar_mensagem("Erro", "Pessoa não encontrada.", tipo="erro")
            return

        # Cria uma janela modal para visualização
        janela = tk.Toplevel(self.master)
        janela.title("Visualizar Pessoa Física")
        janela.transient(self.master)
        janela.grab_set()

        # Centraliza a janela
        largura = 600
        altura = 400
        pos_x = self.master.winfo_rootx() + (self.master.winfo_width() - largura) // 2
        pos_y = self.master.winfo_rooty() + (self.master.winfo_height() - altura) // 2
        janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        # Cria o formulário de visualização
        form = PessoaFisicaForm(
            janela,
            callback_salvar=janela.destroy,
            callback_cancelar=janela.destroy,
            pessoa=pessoa,
        )
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Desabilita os campos para visualização
        for nome, info in form.campos.items():
            info["widget"].configure(state="disabled")

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
        """Abre o formulário para editar a pessoa selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione uma pessoa para editar.", tipo="aviso"
            )
            return

        # Busca a pessoa selecionada
        pessoa = buscar_pessoa_por_id(id_selecao)
        if not pessoa:
            mostrar_mensagem("Erro", "Pessoa não encontrada.", tipo="erro")
            return

        # Oculta o frame principal
        self.frame.pack_forget()

        # Cria e exibe o formulário de edição
        self.formulario = PessoaFisicaForm(
            self.frame_formulario,
            callback_salvar=self.salvar_formulario,
            callback_cancelar=self.cancelar_formulario,
            pessoa=pessoa,
        )
        self.formulario.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.frame_formulario.pack(fill=tk.BOTH, expand=True)

    def excluir(self):
        """Exclui a pessoa selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione uma pessoa para excluir.", tipo="aviso"
            )
            return

        # Confirma a exclusão
        if mostrar_mensagem(
            "Confirmação", "Deseja realmente excluir esta pessoa?", tipo="pergunta"
        ):
            try:
                excluir_pessoa_fisica(id_selecao)
                mostrar_mensagem(
                    "Sucesso", "Pessoa excluída com sucesso!", tipo="sucesso"
                )
                self.carregar_dados()
            except ValueError as e:
                mostrar_mensagem("Erro", str(e), tipo="erro")

    def ver_contratos(self):
        """Abre uma janela para visualizar os contratos da pessoa selecionada"""
        id_selecao = self.tabela.obter_selecao()
        if not id_selecao:
            mostrar_mensagem(
                "Atenção", "Selecione uma pessoa para ver seus contratos.", tipo="aviso"
            )
            return

        # Busca a pessoa selecionada
        pessoa = buscar_pessoa_por_id(id_selecao)
        if not pessoa:
            mostrar_mensagem("Erro", "Pessoa não encontrada.", tipo="erro")
            return

        # Busca os contratos da pessoa
        contratos = listar_contratos_por_pessoa(id_selecao)

        # Cria uma janela modal para exibir os contratos
        janela = tk.Toplevel(self.master)
        janela.title(f"Contratos de {pessoa[1]}")
        janela.transient(self.master)
        janela.grab_set()

        # Maximiza a janela
        janela.state("zoomed")

        # Frame principal
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(frame, text=f"Contratos de {pessoa[1]}", style="Titulo.TLabel").pack(
            anchor=tk.W, pady=(0, 10)
        )

        # Se não houver contratos
        if not contratos:
            ttk.Label(
                frame,
                text="Esta pessoa não possui contratos cadastrados.",
                style="Info.TLabel",
            ).pack(pady=20)
            criar_botao(frame, "Fechar", janela.destroy, "Primario", 15).pack(
                side=tk.BOTTOM, anchor=tk.E
            )
            return

        # Tabela de contratos
        colunas = [
            "id",
            "modalidade",
            "numero_contrato",
            "vigencia_inicial",
            "vigencia_final",
            "status_contrato",
            "total_contrato",
        ]
        titulos = {
            "id": "ID",
            "modalidade": "Modalidade",
            "numero_contrato": "Número do Contrato",
            "vigencia_inicial": "Início Vigência",
            "vigencia_final": "Fim Vigência",
            "status_contrato": "Status",
            "total_contrato": "Valor Total (R$)",
        }

        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True)

        # Carregar os contratos na tabela
        for contrato in contratos:
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

            valores = {
                "id": contrato[0],
                "modalidade": contrato[11],
                "numero_contrato": contrato[13],
                "vigencia_inicial": contrato[14],
                "vigencia_final": contrato[15],
                "status_contrato": status_exibicao,
                "total_contrato": valor_formatado,
            }
            tabela.adicionar_linha(valores, str(contrato[0]))

        # Botão para fechar
        criar_botao(frame, "Fechar", janela.destroy, "Primario", 15).pack(
            side=tk.BOTTOM, anchor=tk.E, pady=(10, 0)
        )

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
