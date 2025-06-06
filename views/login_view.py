# Login View.Py
import tkinter as tk
from tkinter import ttk
from utils.ui_utils import Cores, Estilos, mostrar_mensagem, criar_botao


class LoginView:
    """Tela de login do sistema"""

    def __init__(self, master, login_callback):
        """
        Args:
            master: widget pai
            login_callback: função para verificar as credenciais
        """
        self.master = master
        self.login_callback = login_callback

        # Configuração da janela
        self.master.title("Login - SISPROJ - PESSOA FÍSICA")
        self.master.geometry("400x450")
        self.master.resizable(False, False)

        # Configura estilos
        Estilos.configurar()

        # Frame principal
        self.frame = ttk.Frame(master, padding=20, style="CardBorda.TFrame")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Logo/Título
        self.criar_cabecalho()

        # Formulário
        self.criar_formulario()

        # Rodapé
        self.criar_rodape()

    def criar_cabecalho(self):
        """Cria o cabeçalho com logo e título"""
        frame_cabecalho = ttk.Frame(self.frame, style="Card.TFrame")
        frame_cabecalho.pack(fill=tk.X, pady=(20, 30))

        # Logo (pode ser substituído por uma imagem real)
        canvas = tk.Canvas(
            frame_cabecalho,
            width=80,
            height=80,
            bg=Cores.PRIMARIA,
            highlightthickness=0,
        )
        canvas.pack()

        # Texto no logo
        canvas.create_text(
            40, 40, text="PF", fill=Cores.TEXTO_CLARO, font=("Segoe UI", 24, "bold")
        )

        # Título
        ttk.Label(
            frame_cabecalho, text="SISPROJ - PESSOA FÍSICA", style="Titulo.TLabel"
        ).pack(pady=(10, 0))

        ttk.Label(
            frame_cabecalho, text="Faça login para continuar", style="TLabel"
        ).pack()

    def criar_formulario(self):
        """Cria o formulário de login"""
        frame_form = ttk.Frame(self.frame, style="Card.TFrame")
        frame_form.pack(fill=tk.X, pady=10)

        # Campo de usuário
        ttk.Label(frame_form, text="Usuário:", style="TLabel").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.username_entry = ttk.Entry(frame_form, width=40)
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.focus()

        # Campo de senha
        ttk.Label(frame_form, text="Senha:", style="TLabel").pack(
            anchor=tk.W, pady=(0, 5)
        )
        self.password_entry = ttk.Entry(frame_form, show="*", width=40)
        self.password_entry.pack(fill=tk.X)
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        # Botão de login usando a nova função
        criar_botao(frame_form, "Entrar", self.attempt_login, "Primario", 20).pack(
            pady=(30, 0)
        )

    def criar_rodape(self):
        """Cria o rodapé com informações adicionais"""
        frame_rodape = ttk.Frame(self.frame, style="Card.TFrame")
        frame_rodape.pack(fill=tk.X, side=tk.BOTTOM, pady=20)

        ttk.Separator(frame_rodape).pack(fill=tk.X, pady=(0, 10))
        ttk.Label(
            frame_rodape, text="© 2025 SISPROJ - PESSOA FÍSICA - v1.0", style="TLabel"
        ).pack()

    def attempt_login(self):
        """Tenta fazer login com as credenciais fornecidas"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            mostrar_mensagem("Erro", "Preencha usuário e senha.", tipo="erro")
            return

        self.login_callback(username, password)
