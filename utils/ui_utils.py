# Ui Utils.Py
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkFont


class Cores:
    """Classe com definições de cores para a interface do sistema"""

    # Paleta de cores moderna com melhor contraste
    PRIMARIA = "#2E7D32"  # Verde escuro para pessoa física
    SECUNDARIA = "#4CAF50"  # Verde médio
    ALERTA = "#FF9800"  # Laranja para alertas
    PERIGO = "#D32F2F"  # Vermelho para ações destrutivas
    SUCESSO = "#388E3C"  # Verde escuro para confirmações
    BACKGROUND = "#FFFFFF"  # Fundo branco para tema claro
    BACKGROUND_CLARO = "#F9F9F9"  # Cinza muito claro para cards e frames
    BACKGROUND_ESCURO = "#EEEEEE"  # Cinza claro para elementos secundários
    TEXTO = "#212121"  # Quase preto para texto principal em fundo claro
    TEXTO_CLARO = "#FFFFFF"  # Branco para texto em fundo escuro
    TEXTO_SECUNDARIO = "#757575"  # Cinza para texto secundário
    DETALHE = "#1B5E20"  # Verde escuro para detalhes
    BORDA = "#E0E0E0"  # Cinza claro para bordas

    # Cores específicas para botões com melhor contraste
    BOTAO_PRIMARIO_FUNDO = "#2E7D32"  # Verde escuro
    BOTAO_PRIMARIO_TEXTO = "#FFFFFF"  # Branco
    BOTAO_PRIMARIO_HOVER = "#1B5E20"  # Verde mais escuro para hover

    BOTAO_SECUNDARIO_FUNDO = "#757575"  # Cinza médio
    BOTAO_SECUNDARIO_TEXTO = "#FFFFFF"  # Branco
    BOTAO_SECUNDARIO_HOVER = "#616161"  # Cinza escuro para hover

    BOTAO_PERIGO_FUNDO = "#D32F2F"  # Vermelho
    BOTAO_PERIGO_TEXTO = "#FFFFFF"  # Branco
    BOTAO_PERIGO_HOVER = "#B71C1C"  # Vermelho escuro para hover


class Estilos:
    """Classe para configurar estilos padrão para a aplicação"""

    @staticmethod
    def configurar():
        """Configura os estilos padrão para a aplicação"""
        estilo = ttk.Style()

        # Configura cor de fundo global
        estilo.configure("TFrame", background=Cores.BACKGROUND)
        estilo.configure("TLabel", background=Cores.BACKGROUND, foreground=Cores.TEXTO)

        # Configuração padrão para botões com melhor contraste
        estilo.map(
            "TButton",
            foreground=[
                ("pressed", Cores.BOTAO_PRIMARIO_TEXTO),
                ("active", Cores.BOTAO_PRIMARIO_TEXTO),
                ("!disabled", Cores.BOTAO_PRIMARIO_TEXTO),
            ],
            background=[
                ("pressed", Cores.BOTAO_PRIMARIO_HOVER),
                ("active", Cores.BOTAO_PRIMARIO_HOVER),
                ("!disabled", Cores.BOTAO_PRIMARIO_FUNDO),
            ],
        )
        estilo.configure(
            "TButton",
            background=Cores.BOTAO_PRIMARIO_FUNDO,
            foreground=Cores.BOTAO_PRIMARIO_TEXTO,
            relief="flat",
            font=("Segoe UI", 10),
        )

        # Entradas de texto e componentes de formulário
        estilo.configure(
            "TEntry",
            fieldbackground=Cores.BACKGROUND_CLARO,
            foreground=Cores.TEXTO,
            borderwidth=1,
        )
        estilo.configure(
            "TCombobox",
            fieldbackground=Cores.BACKGROUND_CLARO,
            foreground=Cores.TEXTO,
            borderwidth=1,
        )
        estilo.configure(
            "TSpinbox",
            fieldbackground=Cores.BACKGROUND_CLARO,
            foreground=Cores.TEXTO,
            borderwidth=1,
        )

        # Notebooks e tabs
        estilo.configure("TNotebook", background=Cores.BACKGROUND)

        # Estilo para abas normais
        estilo.configure(
            "TNotebook.Tab",
            background=Cores.BACKGROUND_CLARO,
            foreground=Cores.TEXTO,
            padding=[10, 5],
            font=("Segoe UI", 10),
        )

        # Estilo para abas selecionadas
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", Cores.PRIMARIA)],
            foreground=[("selected", Cores.TEXTO_CLARO)],
            font=[("selected", ("Segoe UI", 10, "bold"))],
        )

        # Configura estilo para botões primários
        estilo.map(
            "Primario.TButton",
            foreground=[
                ("pressed", Cores.BOTAO_PRIMARIO_TEXTO),
                ("active", Cores.BOTAO_PRIMARIO_TEXTO),
                ("!disabled", Cores.BOTAO_PRIMARIO_TEXTO),
            ],
            background=[
                ("pressed", Cores.BOTAO_PRIMARIO_HOVER),
                ("active", Cores.BOTAO_PRIMARIO_HOVER),
                ("!disabled", Cores.BOTAO_PRIMARIO_FUNDO),
            ],
        )
        estilo.configure(
            "Primario.TButton",
            background=Cores.BOTAO_PRIMARIO_FUNDO,
            foreground=Cores.BOTAO_PRIMARIO_TEXTO,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=[10, 5],
        )

        # Configura estilo para botões secundários
        estilo.map(
            "Secundario.TButton",
            foreground=[
                ("pressed", Cores.BOTAO_SECUNDARIO_TEXTO),
                ("active", Cores.BOTAO_SECUNDARIO_TEXTO),
                ("!disabled", Cores.BOTAO_SECUNDARIO_TEXTO),
            ],
            background=[
                ("pressed", Cores.BOTAO_SECUNDARIO_HOVER),
                ("active", Cores.BOTAO_SECUNDARIO_HOVER),
                ("!disabled", Cores.BOTAO_SECUNDARIO_FUNDO),
            ],
        )
        estilo.configure(
            "Secundario.TButton",
            background=Cores.BOTAO_SECUNDARIO_FUNDO,
            foreground=Cores.BOTAO_SECUNDARIO_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            padding=[10, 5],
        )

        # Configura estilo para botões de perigo
        estilo.map(
            "Perigo.TButton",
            foreground=[
                ("pressed", Cores.BOTAO_PERIGO_TEXTO),
                ("active", Cores.BOTAO_PERIGO_TEXTO),
                ("!disabled", Cores.BOTAO_PERIGO_TEXTO),
            ],
            background=[
                ("pressed", Cores.BOTAO_PERIGO_HOVER),
                ("active", Cores.BOTAO_PERIGO_HOVER),
                ("!disabled", Cores.BOTAO_PERIGO_FUNDO),
            ],
        )
        estilo.configure(
            "Perigo.TButton",
            background=Cores.BOTAO_PERIGO_FUNDO,
            foreground=Cores.BOTAO_PERIGO_TEXTO,
            font=("Segoe UI", 10),
            relief="flat",
            padding=[10, 5],
        )

        # Configura estilo para frames
        estilo.configure("Card.TFrame", background=Cores.BACKGROUND)

        # Configura estilo para frames com borda (usado apenas para frames principais)
        estilo.configure(
            "CardBorda.TFrame",
            background=Cores.BACKGROUND,
            borderwidth=0,
            relief="flat",
        )

        # Configura estilo para labels
        estilo.configure(
            "Titulo.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground=Cores.PRIMARIA,
            background=Cores.BACKGROUND,
        )

        estilo.configure(
            "Subtitulo.TLabel",
            font=("Segoe UI", 12, "bold"),
            foreground=Cores.TEXTO,
            background=Cores.BACKGROUND,
        )

        # Info label para mensagens informativas
        estilo.configure(
            "Info.TLabel",
            font=("Segoe UI", 10, "italic"),
            foreground=Cores.TEXTO_SECUNDARIO,
            background=Cores.BACKGROUND,
        )

        # Configura estilo para treeview (tabelas)
        estilo.configure(
            "Treeview",
            background=Cores.BACKGROUND,
            foreground=Cores.TEXTO,
            fieldbackground=Cores.BACKGROUND,
            rowheight=30,
        )

        estilo.map(
            "Treeview",
            background=[("selected", Cores.PRIMARIA)],
            foreground=[("selected", Cores.TEXTO_CLARO)],
        )

        estilo.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=Cores.PRIMARIA,
            foreground=Cores.TEXTO,
            relief="flat",
        )

        # Configura estilo para separadores
        estilo.configure("TSeparator", background=Cores.BORDA)


class FormularioBase(ttk.Frame):
    """Classe base para formulários padronizados"""

    def __init__(self, master, titulo, largura=600):
        super().__init__(master, style="CardBorda.TFrame", padding=15)
        self.titulo = titulo
        self.largura = largura
        self.campos = {}
        self.criar_cabecalho()

    def criar_cabecalho(self):
        """Cria o título do formulário"""
        if self.titulo:
            frame_titulo = ttk.Frame(self)
            frame_titulo.pack(fill=tk.X, pady=(0, 15))

            ttk.Label(frame_titulo, text=self.titulo, style="Titulo.TLabel").pack(
                anchor=tk.W
            )
            ttk.Separator(frame_titulo).pack(fill=tk.X, pady=(8, 0))

    def adicionar_campo_customizado(
        self, nome, label, widget_customizado, required=False
    ):
        """Adiciona um campo customizado ao formulário

        Args:
            nome: identificador do campo
            label: rótulo visível ao usuário
            widget_customizado: widget já criado para ser adicionado
            required: se o campo é obrigatório
        """
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, pady=5)

        # Label do campo
        lbl = ttk.Label(
            frame, text=f"{label}{'*' if required else ''}:", width=20, anchor=tk.W
        )
        lbl.pack(side=tk.LEFT)

        # Adiciona o widget customizado
        widget_customizado.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Armazena referência ao campo
        self.campos[nome] = {
            "widget": widget_customizado,
            "tipo": "customizado",
            "required": required,
        }

    def adicionar_campo(
        self, nome, label, tipo="texto", opcoes=None, padrao=None, required=False
    ):
        """Adiciona um campo ao formulário

        Args:
            nome: identificador do campo
            label: rótulo visível ao usuário
            tipo: tipo do campo (texto, data, numero, senha, opcoes, checkbox, texto_longo)
            opcoes: lista de opções para campos do tipo opcoes
            padrao: valor padrão
            required: se o campo é obrigatório
        """
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, pady=5)

        # Label do campo
        lbl = ttk.Label(
            frame, text=f"{label}{'*' if required else ''}:", width=20, anchor=tk.W
        )
        lbl.pack(side=tk.LEFT)

        # Entrada de dados conforme o tipo
        if tipo == "texto":
            entrada = ttk.Entry(frame, width=40)
            entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif tipo == "senha":
            entrada = ttk.Entry(frame, width=40, show="*")
            entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif tipo == "data":
            entrada = ttk.Entry(frame, width=15)
            entrada.pack(side=tk.LEFT)
            ttk.Label(frame, text="Formato: DD/MM/AAAA", style="Info.TLabel").pack(
                side=tk.LEFT, padx=5
            )
        elif tipo == "numero":
            entrada = ttk.Entry(frame, width=15)
            entrada.pack(side=tk.LEFT)
        elif tipo == "opcoes" and opcoes:
            var = tk.StringVar(value=padrao if padrao else opcoes[0])
            entrada = ttk.Combobox(
                frame, values=opcoes, textvariable=var, state="readonly", width=38
            )
            entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)
        elif tipo == "checkbox":
            var = tk.BooleanVar(value=padrao if padrao is not None else False)
            entrada = ttk.Checkbutton(frame, variable=var)
            entrada.pack(side=tk.LEFT)
        elif tipo == "texto_longo":
            entrada = tk.Text(frame, width=38, height=4)
            entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Define valor padrão se fornecido
        if padrao and tipo not in ["opcoes", "texto_longo", "checkbox"]:
            entrada.insert(0, padrao)
        elif padrao and tipo == "texto_longo":
            entrada.insert("1.0", padrao)

        # Armazena referência ao campo
        self.campos[nome] = {"widget": entrada, "tipo": tipo, "required": required}

    def obter_valores(self):
        """Retorna um dicionário com os valores dos campos"""
        valores = {}
        for nome, info in self.campos.items():
            widget = info["widget"]
            tipo = info["tipo"]

            if tipo == "texto_longo":
                valor = widget.get("1.0", tk.END).strip()
            elif tipo == "opcoes":
                valor = widget.get()
            elif tipo == "checkbox":
                try:
                    # First try to get the var from the widget directly
                    valor = widget.var.get()
                except AttributeError:
                    # If that fails, check if we stored it in the campo dictionary
                    campo = self.campos[nome]
                    if "var" in campo:
                        valor = campo["var"].get()
                    else:
                        # Last resort, try to get the value directly from the widget
                        try:
                            valor = widget.get()
                        except (AttributeError, tk.TclError):
                            # If all else fails, default to False
                            valor = False
            else:
                valor = widget.get().strip()

            valores[nome] = valor

        return valores

    def validar(self):
        """Valida se todos os campos obrigatórios foram preenchidos"""
        for nome, info in self.campos.items():
            if info["required"]:
                widget = info["widget"]
                tipo = info["tipo"]

                if tipo == "texto_longo":
                    valor = widget.get("1.0", tk.END).strip()
                elif tipo == "checkbox":
                    valor = True  # Checkbox é sempre válido
                else:
                    valor = widget.get().strip()

                if not valor:
                    return False, f"O campo '{nome}' é obrigatório."

        return True, ""

    def limpar(self):
        """Limpa todos os campos do formulário"""
        for nome, info in self.campos.items():
            widget = info["widget"]
            tipo = info["tipo"]

            if tipo == "texto_longo":
                widget.delete("1.0", tk.END)
            elif tipo == "opcoes":
                widget.current(0)
            elif tipo == "checkbox":
                widget.var.set(False)
            else:
                widget.delete(0, tk.END)


class TabelaBase(ttk.Frame):
    """Classe base para tabelas padronizadas"""

    def __init__(self, master, colunas, titulos=None):
        """
        Args:
            master: widget pai
            colunas: lista de identificadores de colunas
            titulos: dicionário mapeando colunas para títulos visíveis
        """
        super().__init__(master, style="CardBorda.TFrame", padding=15)
        self.colunas = colunas
        self.titulos = titulos or {
            col: col.replace("_", " ").title() for col in colunas
        }

        # Cria a tabela
        self.criar_tabela()

    def criar_tabela(self):
        """Cria a estrutura da tabela"""
        # Frame com barra de rolagem
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True)

        # Barra de rolagem vertical
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de rolagem horizontal
        h_scrollbar = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview (tabela)
        self.tree = ttk.Treeview(
            frame,
            columns=self.colunas,
            show="headings",
            yscrollcommand=scrollbar.set,
            xscrollcommand=h_scrollbar.set,
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Configura as barras de rolagem
        scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)

        # Configura as colunas
        for col in self.colunas:
            self.tree.heading(col, text=self.titulos[col])
            # Ajusta largura baseada no título
            largura = max(100, len(self.titulos[col]) * 10)
            self.tree.column(col, width=largura, minwidth=50)

        # Adiciona estilo de linhas alternadas para melhor legibilidade
        self.tree.tag_configure("odd", background=Cores.BACKGROUND_CLARO)
        self.tree.tag_configure("even", background=Cores.BACKGROUND)

    def adicionar_linha(self, valores, id=None):
        """Adiciona uma linha à tabela

        Args:
            valores: dicionário de valores para as colunas
            id: identificador da linha (opcional)
        """
        valores_lista = [valores.get(col, "") for col in self.colunas]

        # Aplica estilo de linha alternada
        row_count = len(self.tree.get_children())
        tag = "even" if row_count % 2 == 0 else "odd"

        return self.tree.insert("", tk.END, values=valores_lista, iid=id, tags=(tag,))

    def atualizar_linha(self, id, valores):
        """Atualiza uma linha existente

        Args:
            id: identificador da linha
            valores: dicionário de valores para as colunas
        """
        valores_lista = [valores.get(col, "") for col in self.colunas]
        self.tree.item(id, values=valores_lista)

    def remover_linha(self, id):
        """Remove uma linha da tabela

        Args:
            id: identificador da linha
        """
        self.tree.delete(id)

    def limpar(self):
        """Remove todas as linhas da tabela"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def obter_selecao(self):
        """Retorna o id da linha selecionada ou None"""
        selecao = self.tree.selection()
        if selecao:
            return selecao[0]
        return None

    def obter_valores_selecao(self):
        """Retorna os valores da linha selecionada ou None"""
        id = self.obter_selecao()
        if id:
            valores = self.tree.item(id, "values")
            return dict(zip(self.colunas, valores))
        return None


class Menu:
    """Classe para criar menu de navegação lateral"""

    def __init__(self, master, itens):
        """
        Args:
            master: widget pai
            itens: lista de dicionários com {'texto': 'texto do botão', 'comando': função, 'icone': 'emoji ou símbolo'}
        """
        self.frame = ttk.Frame(master, style="CardBorda.TFrame", width=220)
        self.frame.pack_propagate(False)
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

        # Título do menu
        frame_titulo = ttk.Frame(self.frame, style="Card.TFrame")
        frame_titulo.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(frame_titulo, text="SISPROJ", style="Titulo.TLabel").pack(
            pady=(20, 0)
        )
        ttk.Label(
            frame_titulo,
            text="PESSOA FÍSICA",
            font=("Segoe UI", 10),
            foreground=Cores.TEXTO_SECUNDARIO,
            background=Cores.BACKGROUND,
        ).pack(pady=(0, 15))

        ttk.Separator(self.frame).pack(fill=tk.X, padx=15)

        # Container para os itens do menu
        menu_container = ttk.Frame(self.frame, style="Card.TFrame")
        menu_container.pack(fill=tk.BOTH, expand=True, pady=15)

        # Itens do menu
        for item in itens:
            # Cria um frame para cada item do menu
            frame_item = ttk.Frame(menu_container, style="Card.TFrame")
            frame_item.pack(fill=tk.X, pady=8, padx=15)

            # Cria o botão com ícone e texto alinhado à esquerda
            self.criar_botao_menu(
                frame_item,
                item["texto"],
                item["comando"],
                item.get("icone", ""),
                item.get("estilo", "Primario"),
            )

    def criar_botao_menu(self, master, texto, comando, icone="", estilo="Primario"):
        """Cria um botão de menu com ícone e texto alinhado à esquerda"""
        # Define as cores baseadas no estilo
        if estilo == "Primario":
            bg_color = Cores.BOTAO_PRIMARIO_FUNDO
            fg_color = Cores.BOTAO_PRIMARIO_TEXTO
            hover_color = Cores.BOTAO_PRIMARIO_HOVER
        elif estilo == "Secundario":
            bg_color = Cores.BOTAO_SECUNDARIO_FUNDO
            fg_color = Cores.BOTAO_SECUNDARIO_TEXTO
            hover_color = Cores.BOTAO_SECUNDARIO_HOVER
        else:
            bg_color = Cores.BOTAO_PRIMARIO_FUNDO
            fg_color = Cores.BOTAO_PRIMARIO_TEXTO
            hover_color = Cores.BOTAO_PRIMARIO_HOVER

        # Cria o botão personalizado
        btn = tk.Button(
            master,
            text=f"{icone} {texto}" if icone else texto,
            command=comando,
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 10, "bold" if estilo == "Primario" else "normal"),
            cursor="hand2",
            height=2,
            anchor="w",  # Alinha o texto à esquerda
            padx=10,
        )

        # Adiciona efeitos de hover
        def on_enter(e):
            btn.configure(bg=hover_color)

        def on_leave(e):
            btn.configure(bg=bg_color)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        btn.pack(fill=tk.X, expand=True)
        return btn


def mostrar_mensagem(titulo, mensagem, tipo="info"):
    """Exibe uma mensagem em uma janela modal

    Args:
        titulo: título da janela
        mensagem: texto da mensagem
        tipo: tipo de mensagem (info, erro, aviso, pergunta, sucesso)
    """
    # Personaliza o título para mensagens de sucesso
    if tipo == "sucesso":
        titulo_formatado = f"✓ {titulo}"
    else:
        titulo_formatado = titulo

    if tipo == "info":
        return messagebox.showinfo(titulo_formatado, mensagem)
    elif tipo == "erro":
        return messagebox.showerror(titulo_formatado, mensagem)
    elif tipo == "aviso":
        return messagebox.showwarning(titulo_formatado, mensagem)
    elif tipo == "pergunta":
        return messagebox.askyesno(titulo_formatado, mensagem)
    elif tipo == "sucesso":
        # Usa showinfo mas com título personalizado para indicar sucesso
        return messagebox.showinfo(titulo_formatado, mensagem)


def criar_botao(master, texto, comando, estilo="Primario", largura=20):
    """Cria um botão personalizado com estilo consistente e moderno

    Args:
        master: widget pai
        texto: texto do botão
        comando: função a ser chamada ao clicar
        estilo: estilo do botão (Primario, Secundario, Perigo)
        largura: largura do botão

    Returns:
        O botão criado
    """
    # Define as cores baseadas no estilo
    if estilo == "Primario":
        bg_color = Cores.BOTAO_PRIMARIO_FUNDO
        fg_color = Cores.BOTAO_PRIMARIO_TEXTO
        hover_color = Cores.BOTAO_PRIMARIO_HOVER
    elif estilo == "Secundario":
        bg_color = Cores.BOTAO_SECUNDARIO_FUNDO
        fg_color = Cores.BOTAO_SECUNDARIO_TEXTO
        hover_color = Cores.BOTAO_SECUNDARIO_HOVER
    elif estilo == "Perigo":
        bg_color = Cores.BOTAO_PERIGO_FUNDO
        fg_color = Cores.BOTAO_PERIGO_TEXTO
        hover_color = Cores.BOTAO_PERIGO_HOVER
    else:
        bg_color = Cores.BOTAO_PRIMARIO_FUNDO
        fg_color = Cores.BOTAO_PRIMARIO_TEXTO
        hover_color = Cores.BOTAO_PRIMARIO_HOVER

    # Frame para conter o botão (para efeito de elevação)
    frame = ttk.Frame(master)

    # Cria um botão tk.Button em vez de ttk.Button para ter controle total das cores
    btn = tk.Button(
        frame,
        text=texto,
        command=comando,
        bg=bg_color,
        fg=fg_color,
        activebackground=hover_color,
        activeforeground=fg_color,
        relief="flat",
        borderwidth=0,
        font=("Segoe UI", 10, "bold" if estilo == "Primario" else "normal"),
        cursor="hand2",
        width=largura,
        height=2,
        padx=5,
    )

    # Adiciona efeitos de hover
    def on_enter(e):
        btn.configure(bg=hover_color)

    def on_leave(e):
        btn.configure(bg=bg_color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    btn.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    return frame


def formatar_data(entry, event=None):
    """Formata o campo para data no padrão brasileiro (DD/MM/AAAA)"""
    import re

    texto = entry.get().replace("/", "")
    # Remove caracteres não numéricos
    texto = re.sub(r"[^\d]", "", texto)

    # Limita a 8 dígitos
    if len(texto) > 8:
        texto = texto[:8]

    # Formata conforme a quantidade de dígitos
    if len(texto) > 4:
        texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"
    elif len(texto) > 2:
        texto = f"{texto[:2]}/{texto[2:]}"

    # Atualiza o campo
    entry.delete(0, tk.END)
    entry.insert(0, texto)

    # Valida a data
    if len(texto) == 10:  # Formato completo DD/MM/AAAA
        try:
            dia, mes, ano = map(int, texto.split("/"))
            # Validação básica
            if not (1 <= dia <= 31 and 1 <= mes <= 12 and 1000 <= ano <= 9999):
                entry.config(foreground="red")
            else:
                entry.config(foreground="black")
        except:
            entry.config(foreground="red")

    return True


def formatar_cpf(entry, event=None):
    """Formata o campo para CPF no padrão brasileiro (000.000.000-00)"""
    import re

    texto = entry.get().replace(".", "").replace("-", "")
    # Remove caracteres não numéricos
    texto = re.sub(r"[^\d]", "", texto)

    # Limita a 11 dígitos
    if len(texto) > 11:
        texto = texto[:11]

    # Formata conforme a quantidade de dígitos
    if len(texto) > 9:
        texto = f"{texto[:3]}.{texto[3:6]}.{texto[6:9]}-{texto[9:]}"
    elif len(texto) > 6:
        texto = f"{texto[:3]}.{texto[3:6]}.{texto[6:]}"
    elif len(texto) > 3:
        texto = f"{texto[:3]}.{texto[3:]}"

    # Atualiza o campo
    entry.delete(0, tk.END)
    entry.insert(0, texto)
    return True


def formatar_telefone(entry, event=None):
    """Formata o campo para telefone no padrão brasileiro ((00) 00000-0000)"""
    import re

    texto = (
        entry.get().replace("(", "").replace(")", "").replace(" ", "").replace("-", "")
    )
    # Remove caracteres não numéricos
    texto = re.sub(r"[^\d]", "", texto)

    # Limita a 11 dígitos
    if len(texto) > 11:
        texto = texto[:11]

    # Formata conforme a quantidade de dígitos
    if len(texto) > 6:
        # Celular (11 dígitos) ou fixo (10 dígitos)
        if len(texto) > 10:  # Celular
            texto = f"({texto[:2]}) {texto[2:7]}-{texto[7:]}"
        else:  # Fixo
            texto = f"({texto[:2]}) {texto[2:6]}-{texto[6:]}"
    elif len(texto) > 2:
        texto = f"({texto[:2]}) {texto[2:]}"
    elif len(texto) > 0:
        texto = f"({texto})"

    # Atualiza o campo
    entry.delete(0, tk.END)
    entry.insert(0, texto)
    return True


def formatar_valor_brl(entry, event=None):
    """Formata o campo para valor monetário no padrão brasileiro (R$ 0.000,00)"""
    import re

    texto = entry.get().replace("R$", "").replace(".", "").replace(",", "").strip()
    # Remove caracteres não numéricos
    texto = re.sub(r"[^\d]", "", texto)

    if not texto:
        texto = "0"

    # Converte para float (centavos)
    valor = float(texto) / 100

    # Formata como moeda brasileira
    texto_formatado = (
        f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    # Atualiza o campo
    entry.delete(0, tk.END)
    entry.insert(0, texto_formatado)
    return True


def validar_numerico(event):
    """Permite apenas entrada de caracteres numéricos"""
    if event.char.isdigit() or event.keysym in ("BackSpace", "Delete", "Left", "Right"):
        return True
    return False


def converter_valor_brl_para_float(valor_str):
    """Converte um valor em formato de moeda brasileira (R$ 1.234,56) para float (1234.56)"""
    import re

    if not valor_str:
        return 0.0

    # Se for um número, retorna diretamente
    if isinstance(valor_str, (int, float)):
        return float(valor_str)

    # Remove o símbolo de moeda e espaços
    valor_str = str(valor_str).replace("R$", "").strip()

    # Remove pontos de milhar e substitui vírgula por ponto
    valor_str = valor_str.replace(".", "").replace(",", ".")

    # Remove caracteres não numéricos, exceto ponto decimal
    valor_str = re.sub(r"[^\d.]", "", valor_str)

    try:
        return float(valor_str)
    except ValueError:
        return 0.0
