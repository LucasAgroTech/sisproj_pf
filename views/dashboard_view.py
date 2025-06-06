# Dashboard View.Py
import tkinter as tk
from tkinter import ttk
from utils.ui_utils import Estilos, TabelaBase, Menu, mostrar_mensagem, criar_botao
from utils.session import Session
from controllers.pessoa_fisica_controller import listar_pessoas
from controllers.contrato_pf_controller import listar_contratos
from controllers.produto_pf_controller import listar_produtos
from views.pessoa_fisica_view import PessoaFisicaView
from views.contrato_pf_view import ContratoPFView
from views.produto_pf_view import ProdutoPFView


class DashboardView:
    """Dashboard principal do sistema"""

    def __init__(self, master):
        self.master = master
        self.master.title("Dashboard - SISPROJ - PESSOA FÍSICA")
        self.master.geometry("1200x700")  # Define tamanho inicial da janela

        # Configura estilos
        Estilos.configurar()

        # Frame principal
        self.frame = ttk.Frame(master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Cria menu lateral
        self.criar_menu()

        # Frame de conteúdo (inicialmente mostra o dashboard)
        self.frame_conteudo = ttk.Frame(self.frame, style="CardBorda.TFrame")
        self.frame_conteudo.pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # Mostrar dashboard inicial
        self.mostrar_dashboard()

    def criar_menu(self):
        """Cria o menu lateral"""
        # Itens principais do menu com ícones
        itens_menu = [
            {"texto": "Dashboard", "comando": self.mostrar_dashboard, "icone": "📊"},
            {
                "texto": "Pessoas Físicas",
                "comando": self.mostrar_pessoas_fisicas,
                "icone": "👤",
            },
            {"texto": "Contratos", "comando": self.mostrar_contratos, "icone": "📝"},
            {"texto": "Relatórios", "comando": self.mostrar_relatorios, "icone": "📈"},
        ]

        # Cria o menu com os itens principais
        self.menu = Menu(self.frame, itens_menu)

        # Adiciona o botão Sair de forma mais discreta
        menu_container = self.menu.frame.winfo_children()[
            2
        ]  # Obtém o container dos itens de menu
        ttk.Separator(menu_container).pack(fill=tk.X, padx=15, pady=(15, 15))

        # Cria o botão Sair com estilo secundário (mais discreto) e ícone
        frame_sair = ttk.Frame(menu_container, style="Card.TFrame")
        frame_sair.pack(fill=tk.X, pady=8, padx=15)
        self.menu.criar_botao_menu(frame_sair, "Sair", self.sair, "🚪", "Secundario")

    def limpar_conteudo(self):
        """Limpa o frame de conteúdo"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def mostrar_dashboard(self):
        """Exibe o dashboard com resumo e estatísticas"""
        self.limpar_conteudo()

        # Frame de título
        frame_titulo = ttk.Frame(self.frame_conteudo)
        frame_titulo.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(frame_titulo, text="Dashboard", style="Titulo.TLabel").pack(
            anchor=tk.W
        )
        ttk.Separator(frame_titulo).pack(fill=tk.X, pady=(5, 0))

        # Frame com cards de resumo
        frame_resumo = ttk.Frame(self.frame_conteudo)
        frame_resumo.pack(fill=tk.X, pady=(0, 20))

        # Cria cards com estatísticas
        try:
            self.criar_card_estatistica(
                frame_resumo, "Pessoas Físicas", len(listar_pessoas()), "#388E3C"
            )
            self.criar_card_estatistica(
                frame_resumo, "Contratos", len(listar_contratos()), "#1976D2"
            )
            self.criar_card_estatistica(
                frame_resumo, "Produtos", len(listar_produtos()), "#D32F2F"
            )
        except Exception as e:
            # Se as tabelas ainda não existirem ou houver outro erro
            self.criar_card_estatistica(frame_resumo, "Pessoas Físicas", 0, "#388E3C")
            self.criar_card_estatistica(frame_resumo, "Contratos", 0, "#1976D2")
            self.criar_card_estatistica(frame_resumo, "Produtos", 0, "#D32F2F")

        # Frame com tabelas de atividade recente
        frame_atividade = ttk.Frame(self.frame_conteudo)
        frame_atividade.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Dividir em duas colunas
        frame_col1 = ttk.Frame(frame_atividade)
        frame_col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        frame_col2 = ttk.Frame(frame_atividade)
        frame_col2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Contratos recentes
        self.criar_tabela_contratos_recentes(frame_col1)

        # Produtos recentes
        self.criar_tabela_produtos_recentes(frame_col2)

        # Informações do usuário logado
        usuario = Session.get_user()
        if usuario:
            frame_usuario = ttk.Frame(self.frame_conteudo)
            frame_usuario.pack(fill=tk.X, pady=(10, 0))

            ttk.Label(
                frame_usuario, text=f"Usuário logado: {usuario[1]}", style="TLabel"
            ).pack(side=tk.RIGHT)

    def criar_card_estatistica(self, master, titulo, valor, cor):
        """Cria um card com estatística"""
        frame = ttk.Frame(master, style="CardBorda.TFrame")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # Borda colorida superior
        borda = tk.Frame(frame, background=cor, height=5)
        borda.pack(fill=tk.X)

        # Conteúdo do card
        ttk.Label(frame, text=titulo, font=("Segoe UI", 12)).pack(pady=(15, 5))
        ttk.Label(frame, text=str(valor), font=("Segoe UI", 24, "bold")).pack(
            pady=(5, 15)
        )

    def criar_tabela_contratos_recentes(self, master):
        """Cria tabela com contratos recentes"""
        frame = ttk.Frame(master)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Contratos Recentes", style="Subtitulo.TLabel").pack(
            anchor=tk.W, pady=(0, 5)
        )

        # Tabela de contratos
        colunas = [
            "id",
            "nome_completo",
            "modalidade",
            "status_contrato",
            "total_contrato",
        ]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome",
            "modalidade": "Modalidade",
            "status_contrato": "Status",
            "total_contrato": "Valor (R$)",
        }

        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True)

        try:
            # Carregar dados (limitado aos 5 mais recentes)
            contratos = listar_contratos()
            for i, contrato in enumerate(
                contratos[:5] if len(contratos) >= 5 else contratos
            ):
                try:
                    # Formatar valor monetário
                    valor_total = float(contrato[22]) if contrato[22] else 0.0
                    valor_formatado = (
                        f"R$ {valor_total:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )

                    # Extrair nome da pessoa
                    nome_completo = contrato[-1] if len(contrato) > 23 else "N/A"

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

                    valores = {
                        "id": contrato[0],
                        "nome_completo": nome_completo,
                        "modalidade": contrato[11],
                        "status_contrato": status_exibicao,
                        "total_contrato": valor_formatado,
                    }
                    tabela.adicionar_linha(valores)
                except Exception as e:
                    print(f"Erro ao processar contrato: {e}")
        except Exception as e:
            print(f"Erro ao listar contratos: {e}")

        # Botão para ver todos
        criar_botao(frame, "Ver Todos", self.mostrar_contratos, "Secundario").pack(
            anchor=tk.E, pady=(5, 0)
        )

    def criar_tabela_produtos_recentes(self, master):
        """Cria tabela com produtos recentes"""
        frame = ttk.Frame(master)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Produtos Recentes", style="Subtitulo.TLabel").pack(
            anchor=tk.W, pady=(0, 5)
        )

        # Tabela de produtos
        colunas = ["id", "nome_completo", "titulo", "status", "valor"]
        titulos = {
            "id": "ID",
            "nome_completo": "Nome do Contratado",
            "titulo": "Título",
            "status": "Status",
            "valor": "Valor (R$)",
        }

        tabela = TabelaBase(frame, colunas, titulos)
        tabela.pack(fill=tk.BOTH, expand=True)

        try:
            # Carregar dados (limitado aos 5 mais recentes)
            produtos = listar_produtos()
            for i, produto in enumerate(
                produtos[:5] if len(produtos) >= 5 else produtos
            ):
                try:
                    # Formatar valor monetário
                    valor = float(produto[7]) if produto[7] else 0.0
                    valor_formatado = (
                        f"R$ {valor:,.2f}".replace(",", "X")
                        .replace(".", ",")
                        .replace("X", ".")
                    )

                    # Extrair nome da pessoa
                    nome_completo = produto[-1] if len(produto) > 8 else "N/A"

                    # Status para exibição
                    status_map = {
                        "programado": "Programado",
                        "em_execucao": "Em Execução",
                        "entregue": "Entregue",
                        "cancelado": "Cancelado",
                    }
                    status_exibicao = status_map.get(produto[5], produto[5])

                    valores = {
                        "id": produto[0],
                        "nome_completo": nome_completo,
                        "titulo": produto[6],
                        "status": status_exibicao,
                        "valor": valor_formatado,
                    }
                    tabela.adicionar_linha(valores)
                except Exception as e:
                    print(f"Erro ao processar produto: {e}")
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")

        # Botão para ver produtos através dos contratos
        criar_botao(frame, "Ver Contratos", self.mostrar_contratos, "Secundario").pack(
            anchor=tk.E, pady=(5, 0)
        )

    def mostrar_pessoas_fisicas(self):
        """Abre a tela de gestão de pessoas físicas"""
        self.limpar_conteudo()
        PessoaFisicaView(self.frame_conteudo)

    def mostrar_contratos(self):
        """Abre a tela de gestão de contratos"""
        self.limpar_conteudo()
        ContratoPFView(self.frame_conteudo)

    def mostrar_produtos(self):
        """Abre a tela de gestão de produtos"""
        self.limpar_conteudo()
        ProdutoPFView(self.frame_conteudo)

    def mostrar_relatorios(self):
        """Abre a tela de relatórios"""
        self.limpar_conteudo()
        mostrar_mensagem(
            "Em desenvolvimento",
            "Esta funcionalidade será implementada em breve.",
            tipo="info",
        )
        self.mostrar_dashboard()

    def sair(self):
        """Fecha a aplicação"""
        if mostrar_mensagem(
            "Confirmação", "Deseja realmente sair da aplicação?", tipo="pergunta"
        ):
            Session.logout()
            self.master.destroy()
