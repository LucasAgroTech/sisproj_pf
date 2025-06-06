# Main View for ContratoPF
import tkinter as tk
from tkinter import ttk

from controllers.contrato_pf_controller import (
    listar_contratos,
    buscar_contrato_por_id,
    excluir_contrato,
)
from utils.ui_utils import (
    TabelaBase,
    criar_botao,
    mostrar_mensagem,
    Estilos,
    formatar_data,
    formatar_valor_brl,
)
from views.contrato_pf.contract_form import ContratoPFForm


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
            frame_cabecalho, "+ Novo Contrato", self.adicionar, "Primario", 15
        ).pack(side=tk.RIGHT)

        # Frame principal para pesquisa e filtros
        frame_pesquisa_filtros = ttk.Frame(self.frame)
        frame_pesquisa_filtros.pack(fill=tk.X, pady=(0, 10))

        # Frame de pesquisa (parte superior)
        frame_pesquisa = ttk.Frame(frame_pesquisa_filtros)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        self.pesquisa_entry = ttk.Entry(frame_pesquisa, width=40)
        self.pesquisa_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.pesquisa_entry.bind("<Return>", lambda e: self.pesquisar())

        # Botões de pesquisa mais discretos
        btn_frame = ttk.Frame(frame_pesquisa)
        btn_frame.pack(side=tk.RIGHT)
        
        # Botão para mostrar/ocultar filtros
        self.filtros_visiveis = tk.BooleanVar(value=False)
        self.btn_toggle_filtros = tk.Button(
            btn_frame,
            text="🔍 Filtros",
            command=self.toggle_filtros,
            bg="#f0f0f0",
            fg="#333333",
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.btn_toggle_filtros.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botões de buscar e limpar mais discretos
        self.btn_buscar = tk.Button(
            btn_frame,
            text="Buscar",
            command=self.pesquisar,
            bg="#2E7D32",
            fg="#FFFFFF",
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.btn_buscar.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_limpar = tk.Button(
            btn_frame,
            text="Limpar",
            command=self.limpar_pesquisa,
            bg="#757575",
            fg="#FFFFFF",
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.btn_limpar.pack(side=tk.LEFT)
        
        # Adicionar efeitos de hover para os botões
        for btn, hover_color in [(self.btn_buscar, "#1B5E20"), (self.btn_limpar, "#616161"), (self.btn_toggle_filtros, "#e0e0e0")]:
            btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
            if btn == self.btn_buscar:
                default_color = "#2E7D32"
            elif btn == self.btn_limpar:
                default_color = "#757575"
            else:
                default_color = "#f0f0f0"
            btn.bind("<Leave>", lambda e, b=btn, c=default_color: b.config(bg=c))

        # Separador visual removido
        
        # Frame de filtros (inicialmente oculto)
        self.frame_filtros = ttk.Frame(frame_pesquisa_filtros)
        
        # Primeira linha de filtros
        frame_filtros_linha1 = ttk.Frame(self.frame_filtros)
        frame_filtros_linha1.pack(fill=tk.X, pady=(5, 2))
        
        # Filtro por modalidade
        ttk.Label(frame_filtros_linha1, text="Modalidade:", width=12, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_modalidade = ttk.Combobox(
            frame_filtros_linha1, values=["Todos", "BOLSA", "PRODUTO", "RPA", "CLT"], width=15
        )
        self.filtro_modalidade.current(0)
        self.filtro_modalidade.pack(side=tk.LEFT, padx=(0, 15))
        
        # Filtro por status
        ttk.Label(frame_filtros_linha1, text="Status:", width=8, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_status = ttk.Combobox(
            frame_filtros_linha1,
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
        self.filtro_status.pack(side=tk.LEFT)
        
        # Segunda linha de filtros
        frame_filtros_linha2 = ttk.Frame(self.frame_filtros)
        frame_filtros_linha2.pack(fill=tk.X, pady=(2, 5))
        
        # Filtro por período de vigência
        ttk.Label(frame_filtros_linha2, text="Vigência de:", width=12, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_vigencia_inicial = ttk.Entry(frame_filtros_linha2, width=12)
        self.filtro_vigencia_inicial.pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_vigencia_inicial.bind("<KeyRelease>", lambda e: formatar_data(self.filtro_vigencia_inicial, e))
        
        ttk.Label(frame_filtros_linha2, text="até:", width=4, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_vigencia_final = ttk.Entry(frame_filtros_linha2, width=12)
        self.filtro_vigencia_final.pack(side=tk.LEFT, padx=(0, 15))
        self.filtro_vigencia_final.bind("<KeyRelease>", lambda e: formatar_data(self.filtro_vigencia_final, e))
        
        # Filtro por valor mínimo
        ttk.Label(frame_filtros_linha2, text="Valor mín.:", width=8, anchor=tk.W).pack(side=tk.LEFT, padx=(0, 5))
        self.filtro_valor_minimo = ttk.Entry(frame_filtros_linha2, width=15)
        self.filtro_valor_minimo.pack(side=tk.LEFT)
        self.filtro_valor_minimo.bind("<KeyRelease>", lambda e: formatar_valor_brl(self.filtro_valor_minimo, e))
        
        # Botão para aplicar filtros (mais discreto)
        btn_frame_aplicar = ttk.Frame(self.frame_filtros)
        btn_frame_aplicar.pack(fill=tk.X, pady=(5, 0), anchor=tk.E)
        
        self.btn_aplicar = tk.Button(
            btn_frame_aplicar,
            text="Aplicar Filtros",
            command=self.aplicar_filtros,
            bg="#2E7D32",
            fg="#FFFFFF",
            relief="flat",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=8,
            pady=4,
            cursor="hand2",
        )
        self.btn_aplicar.pack(side=tk.RIGHT)
        
        # Adicionar efeito de hover para o botão aplicar
        self.btn_aplicar.bind("<Enter>", lambda e: self.btn_aplicar.config(bg="#1B5E20"))
        self.btn_aplicar.bind("<Leave>", lambda e: self.btn_aplicar.config(bg="#2E7D32"))

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
            "numero_contrato": "Contrato",
            "vigencia_inicial": "Início Vigência",
            "vigencia_final": "Fim Vigência",
            "status_contrato": "Status",
            "total_contrato": "Valor Total (R$)",
        }

        self.tabela = TabelaBase(self.frame, colunas, titulos)
        self.tabela.pack(fill=tk.BOTH, expand=True)
        
        # Configurar a tabela para usar a largura máxima disponível
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Ocultar a coluna ID
        self.tabela.tree.column("id", width=0, stretch=False)
        
        # Ajustar a largura da coluna nome para ser mais larga
        self.tabela.tree.column("nome_completo", width=300, minwidth=200)
        
        # Reduzir a largura da coluna contrato
        self.tabela.tree.column("numero_contrato", width=120, minwidth=100)
        
        # Ajustar a largura das colunas de vigência
        self.tabela.tree.column("vigencia_inicial", width=110, minwidth=110)
        self.tabela.tree.column("vigencia_final", width=90, minwidth=90)
        
        # Configurar a ordenação por ID
        self.tabela.tree["displaycolumns"] = colunas[1:]  # Oculta a coluna ID do display
        
        # Alinhar todos os títulos e valores à esquerda
        for col in colunas:
            self.tabela.tree.column(col, anchor=tk.W)  # W = West (esquerda)
            self.tabela.tree.heading(col, anchor=tk.W)  # Alinha os cabeçalhos à esquerda também

        # Frame de botões de ação
        frame_acoes = ttk.Frame(self.frame)
        frame_acoes.pack(fill=tk.X, pady=(10, 0))

        criar_botao(frame_acoes, "Visualizar", self.visualizar, "Primario", 15).pack(
            side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Editar", self.editar, "Secundario", 15).pack(
            side=tk.LEFT, padx=(0, 5))
        criar_botao(frame_acoes, "Excluir", self.excluir, "Perigo", 15).pack(
            side=tk.LEFT, padx=(0, 5))
        criar_botao(
            frame_acoes, "Ver Produtos", self.ver_produtos, "Primario", 15
        ).pack(side=tk.LEFT)

        # Formulário (inicialmente oculto)
        self.frame_formulario = ttk.Frame(self.master)

        # Carrega os dados
        self.carregar_dados()

    def carregar_dados(self, filtro=None, filtro_modalidade=None, filtro_status=None, 
                      filtro_vigencia_inicial=None, filtro_vigencia_final=None, filtro_valor_minimo=None):
        """Carrega os dados dos contratos na tabela"""
        self.tabela.limpar()

        # Obter contratos e ordenar por ID
        contratos = listar_contratos()
        contratos.sort(key=lambda x: int(x[0]) if x[0] else 0)  # Ordenar por ID (primeiro campo)

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
                    
            # Filtro por vigência inicial
            if filtro_vigencia_inicial:
                try:
                    # Converter para formato de comparação (YYYY-MM-DD)
                    partes = filtro_vigencia_inicial.split('/')
                    if len(partes) == 3:
                        data_filtro = f"{partes[2]}-{partes[1]}-{partes[0]}"
                        if contrato[14] < data_filtro:
                            continue
                except (ValueError, IndexError):
                    pass
                    
            # Filtro por vigência final
            if filtro_vigencia_final:
                try:
                    # Converter para formato de comparação (YYYY-MM-DD)
                    partes = filtro_vigencia_final.split('/')
                    if len(partes) == 3:
                        data_filtro = f"{partes[2]}-{partes[1]}-{partes[0]}"
                        if contrato[15] > data_filtro:
                            continue
                except (ValueError, IndexError):
                    pass
                    
            # Filtro por valor mínimo
            if filtro_valor_minimo:
                try:
                    # Converter valor do filtro para float
                    from utils.ui_utils import converter_valor_brl_para_float
                    valor_min = converter_valor_brl_para_float(filtro_valor_minimo)
                    valor_contrato = float(contrato[22]) if contrato[22] else 0.0
                    if valor_contrato < valor_min:
                        continue
                except (ValueError, TypeError):
                    pass

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

    def toggle_filtros(self):
        """Mostra ou oculta o painel de filtros"""
        if self.filtros_visiveis.get():
            self.frame_filtros.pack_forget()
            self.filtros_visiveis.set(False)
            self.btn_toggle_filtros.config(text="🔍 Filtros")
        else:
            # Encontrar o frame pai para posicionar corretamente
            parent_frame = self.btn_toggle_filtros.master.master
            self.frame_filtros.pack(fill=tk.X, pady=(0, 5), after=parent_frame)
            self.filtros_visiveis.set(True)
            self.btn_toggle_filtros.config(text="🔍 Ocultar Filtros")

    def pesquisar(self):
        """Filtra os contratos conforme o texto de pesquisa e filtros aplicados"""
        texto = self.pesquisa_entry.get().strip()
        modalidade = (
            self.filtro_modalidade.get()
            if self.filtro_modalidade.get() != "Todos"
            else None
        )
        status = (
            self.filtro_status.get() if self.filtro_status.get() != "Todos" else None
        )
        
        # Novos filtros
        vigencia_inicial = self.filtro_vigencia_inicial.get().strip() if hasattr(self, 'filtro_vigencia_inicial') else ""
        vigencia_final = self.filtro_vigencia_final.get().strip() if hasattr(self, 'filtro_vigencia_final') else ""
        valor_minimo = self.filtro_valor_minimo.get().strip() if hasattr(self, 'filtro_valor_minimo') else ""
        
        self.carregar_dados(texto, modalidade, status, vigencia_inicial, vigencia_final, valor_minimo)

    def limpar_pesquisa(self):
        """Limpa o campo de pesquisa e todos os filtros, recarregando todos os dados"""
        self.pesquisa_entry.delete(0, tk.END)
        self.filtro_modalidade.current(0)
        self.filtro_status.current(0)
        
        # Limpar novos filtros se existirem
        if hasattr(self, 'filtro_vigencia_inicial'):
            self.filtro_vigencia_inicial.delete(0, tk.END)
        if hasattr(self, 'filtro_vigencia_final'):
            self.filtro_vigencia_final.delete(0, tk.END)
        if hasattr(self, 'filtro_valor_minimo'):
            self.filtro_valor_minimo.delete(0, tk.END)
            
        self.carregar_dados()

    def aplicar_filtros(self):
        """Aplica todos os filtros selecionados"""
        self.pesquisar()

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
            # Desabilitar pessoa selector
            form.pessoa_selector.set_state("disabled")

            # Desabilitar campos de formulários
            for formulario in [form.form_demanda, form.form_custeio, form.form_contrato]:
                for nome, info in formulario.campos.items():
                    # Alguns campos podem ser especiais, como o checkbox
                    if info["tipo"] == "checkbox":
                        continue
                    elif info["tipo"] == "texto_longo":
                        info["widget"].configure(state="disabled")
                    else:
                        info["widget"].configure(state="disabled")

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
