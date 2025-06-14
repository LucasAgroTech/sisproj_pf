# Custeio Manager
import tkinter as tk
from tkinter import ttk

from controllers.custeio_controller import CusteioController
from utils.ui_utils import FormularioBase


class CusteioManager:
    """Gerenciador de campos de custeio para contratos"""

    def __init__(self, form_custeio, contrato=None, modo_edicao=False):
        """
        Args:
            form_custeio: FormularioBase onde os campos serão adicionados
            contrato: dados do contrato para edição (opcional)
            modo_edicao: indica se está em modo de edição
        """
        self.form_custeio = form_custeio
        self.contrato = contrato
        self.modo_edicao = modo_edicao
        self.custeio_controller = CusteioController()
        
        # Garantir que o contrato seja uma tupla ou lista válida
        if self.contrato is not None and not isinstance(self.contrato, (list, tuple)):
            print(f"Aviso: contrato não é uma lista ou tupla em CusteioManager: {type(self.contrato)}")
            self.contrato = None
            self.modo_edicao = False

        # Configurar campos de custeio
        self.configurar_campos()
        
        # Configurar eventos de mudança para os filtros hierárquicos
        self.configurar_filtros()
        
        # Forçar atualização dos valores após inicialização
        if self.modo_edicao and self.contrato:
            self.master_after = self.form_custeio.master.after(100, self.forcar_valores_contrato)

    def forcar_valores_contrato(self):
        """Força a atualização dos valores do contrato nos comboboxes após inicialização"""
        try:
            # Garantir que os valores do contrato sejam definidos corretamente
            if self.contrato:
                # Instituição
                if len(self.contrato) > 3 and self.contrato[3]:
                    self.form_custeio.campos["instituicao"]["widget"].set(self.contrato[3])
                
                # Instrumento
                if len(self.contrato) > 4 and self.contrato[4]:
                    self.form_custeio.campos["instrumento"]["widget"].set(self.contrato[4])
                
                # Subprojeto
                if len(self.contrato) > 5 and self.contrato[5]:
                    self.form_custeio.campos["subprojeto"]["widget"].set(self.contrato[5])
                
                # TA
                if len(self.contrato) > 6 and self.contrato[6]:
                    self.form_custeio.campos["ta"]["widget"].set(self.contrato[6])
                
                # PTA
                if len(self.contrato) > 7 and self.contrato[7]:
                    self.form_custeio.campos["pta"]["widget"].set(self.contrato[7])
                
                # Ação
                if len(self.contrato) > 8 and self.contrato[8]:
                    self.form_custeio.campos["acao"]["widget"].set(self.contrato[8])
                
                # Resultado
                if len(self.contrato) > 9 and self.contrato[9]:
                    self.form_custeio.campos["resultado"]["widget"].set(self.contrato[9])
                
                # Meta
                if len(self.contrato) > 10 and self.contrato[10]:
                    self.form_custeio.campos["meta"]["widget"].set(self.contrato[10])
                
                # Aplicar regras de habilitação/desabilitação baseadas na instituição
                if len(self.contrato) > 3 and self.contrato[3]:
                    self.aplicar_regras_instituicao(self.contrato[3])
        except Exception as e:
            print(f"Erro ao forçar valores do contrato no custeio: {e}")

    def configurar_campos(self):
        """Configura os campos de custeio no formulário"""
        # Obter todas as instituições disponíveis
        instituicoes_opcoes = self.custeio_controller.get_institutions()
        if not instituicoes_opcoes:
            instituicoes_opcoes = ["OPAS", "FIOCRUZ"]  # fallback

        # Garantir que a instituição seja uma das opções válidas
        instituicao_padrao = ""
        if self.contrato and len(self.contrato) > 3 and self.contrato[3]:
            instituicao_padrao = self.contrato[3]
            # Garantir que o valor do contrato esteja nas opções
            if instituicao_padrao not in instituicoes_opcoes:
                instituicoes_opcoes.append(instituicao_padrao)
        else:
            instituicao_padrao = instituicoes_opcoes[0] if instituicoes_opcoes else ""

        # Campo Instituição
        self.form_custeio.adicionar_campo(
            "instituicao",
            "Instituição",
            tipo="opcoes",
            opcoes=instituicoes_opcoes,
            padrao=instituicao_padrao,
            required=True,
        )

        # Campo Instrumento (Projeto)
        projetos_iniciais = []
        if instituicao_padrao:
            projetos_iniciais = self.custeio_controller.get_projects(instituicao_padrao)
        
        instrumento_padrao = self.contrato[4] if self.contrato and len(self.contrato) > 4 else ""
        
        # Garantir que o valor original esteja nas opções se for modo edição
        if self.modo_edicao and instrumento_padrao and instrumento_padrao not in projetos_iniciais:
            projetos_iniciais.append(instrumento_padrao)
        
        self.form_custeio.adicionar_campo(
            "instrumento",
            "Instrumento",
            tipo="opcoes",
            opcoes=projetos_iniciais,
            padrao=instrumento_padrao,
        )

        # Campo Subprojeto (3ª posição - puxando da tabela custeio)
        subprojetos_iniciais = []
        if instituicao_padrao and instrumento_padrao:
            subprojetos_iniciais = self.custeio_controller.get_subprojects(instituicao_padrao, instrumento_padrao)
        
        subprojeto_padrao = self.contrato[5] if self.contrato and len(self.contrato) > 5 else ""
        
        # Garantir que o valor original esteja nas opções se for modo edição
        if self.modo_edicao and subprojeto_padrao and subprojeto_padrao not in subprojetos_iniciais:
            subprojetos_iniciais.append(subprojeto_padrao)
        
        self.form_custeio.adicionar_campo(
            "subprojeto",
            "Subprojeto",
            tipo="opcoes",
            opcoes=subprojetos_iniciais,
            padrao=subprojeto_padrao,
        )

        # Campo TA (4ª posição)
        tas_iniciais = []
        if instituicao_padrao and instrumento_padrao:
            # Para OPAS e outras instituições, carregar TAs baseado em instituição + instrumento
            if instituicao_padrao == "OPAS" or instituicao_padrao not in ["FIOCRUZ"]:
                tas_iniciais = self.custeio_controller.get_tas(instituicao_padrao, instrumento_padrao)
        
        ta_padrao = self.contrato[6] if self.contrato and len(self.contrato) > 6 else ""
        
        # Garantir que o valor original esteja nas opções se for modo edição
        if self.modo_edicao and ta_padrao and ta_padrao not in tas_iniciais:
            tas_iniciais.append(ta_padrao)
        
        self.form_custeio.adicionar_campo(
            "ta",
            "TA",
            tipo="opcoes",
            opcoes=tas_iniciais,
            padrao=ta_padrao,
        )

        # Campo Resultado (5ª posição)
        resultados_iniciais = []
        ta_padrao_value = self.contrato[6] if self.contrato and len(self.contrato) > 6 else ""
        if instituicao_padrao and instrumento_padrao and ta_padrao_value:
            # Para OPAS e outras instituições, carregar resultados baseado em instituição + instrumento + TA
            if instituicao_padrao == "OPAS" or instituicao_padrao not in ["FIOCRUZ"]:
                resultados_iniciais = self.custeio_controller.get_results(instituicao_padrao, instrumento_padrao, ta_padrao_value)
        
        resultado_padrao = self.contrato[9] if self.contrato and len(self.contrato) > 9 else ""
        
        # Garantir que o valor original esteja nas opções se for modo edição
        if self.modo_edicao and resultado_padrao and resultado_padrao not in resultados_iniciais:
            resultados_iniciais.append(resultado_padrao)
        
        self.form_custeio.adicionar_campo(
            "resultado",
            "Resultado",
            tipo="opcoes",
            opcoes=resultados_iniciais,
            padrao=resultado_padrao,
        )

        # Campo PTA (6ª posição - mantido como estava, não vem da base de custeio)
        pta_opcoes = ["2022", "2023", "2024", "2025"]
        pta_padrao = self.contrato[7] if self.contrato and len(self.contrato) > 7 else ""
        if pta_padrao and pta_padrao not in pta_opcoes:
            pta_opcoes.append(pta_padrao)
            
        self.form_custeio.adicionar_campo(
            "pta",
            "PTA",
            tipo="opcoes",
            opcoes=pta_opcoes,
            padrao=pta_padrao,
        )

        # Campo Ação (7ª posição - mantido como estava, não vem da base de custeio)
        acao_opcoes = ["01", "02", "03", "04", "05"]
        acao_padrao = self.contrato[8] if self.contrato and len(self.contrato) > 8 else ""
        if acao_padrao and acao_padrao not in acao_opcoes:
            acao_opcoes.append(acao_padrao)
            
        self.form_custeio.adicionar_campo(
            "acao",
            "Ação",
            tipo="opcoes",
            opcoes=acao_opcoes,
            padrao=acao_padrao,
        )

        # Campo Meta (8ª posição - sempre lista de 01 a 35)
        meta_opcoes = [f"{i:02d}" for i in range(1, 36)]  # Lista de 01 até 35
        meta_padrao = self.contrato[10] if self.contrato and len(self.contrato) > 10 else ""
        if meta_padrao and meta_padrao not in meta_opcoes:
            meta_opcoes.append(meta_padrao)
            
        self.form_custeio.adicionar_campo(
            "meta",
            "Meta",
            tipo="opcoes",
            opcoes=meta_opcoes,
            padrao=meta_padrao,
        )

        # Aplicar regras da instituição inicial
        if instituicao_padrao:
            self.aplicar_regras_instituicao(instituicao_padrao)

    def configurar_filtros(self):
        """Configurar eventos de mudança para os filtros hierárquicos de custeio"""
        
        # Obter os widgets dos campos
        instituicao_widget = self.form_custeio.campos["instituicao"]["widget"]
        instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
        subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
        ta_widget = self.form_custeio.campos["ta"]["widget"]
        resultado_widget = self.form_custeio.campos["resultado"]["widget"]
        meta_widget = self.form_custeio.campos["meta"]["widget"]
        
        # Configurar eventos de seleção
        instituicao_widget.bind("<<ComboboxSelected>>", self.on_instituicao_changed)
        instrumento_widget.bind("<<ComboboxSelected>>", self.on_instrumento_changed)
        subprojeto_widget.bind("<<ComboboxSelected>>", self.on_subprojeto_changed)
        ta_widget.bind("<<ComboboxSelected>>", self.on_ta_changed)
        resultado_widget.bind("<<ComboboxSelected>>", self.on_resultado_changed)
        
        # Sincronizar Meta com Subprojeto
        meta_widget.bind("<<ComboboxSelected>>", self.on_meta_changed)

    def aplicar_regras_instituicao(self, instituicao):
        """Aplica regras específicas de habilitação/desabilitação baseadas na instituição"""
        try:
            # Obter widgets dos campos
            subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
            ta_widget = self.form_custeio.campos["ta"]["widget"]
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            pta_widget = self.form_custeio.campos["pta"]["widget"]
            acao_widget = self.form_custeio.campos["acao"]["widget"]
            meta_widget = self.form_custeio.campos["meta"]["widget"]
            
            # Preservar valores atuais antes de aplicar regras
            ta_valor = ta_widget.get()
            resultado_valor = resultado_widget.get()
            pta_valor = pta_widget.get()
            acao_valor = acao_widget.get()
            meta_valor = meta_widget.get()
            subprojeto_valor = subprojeto_widget.get()
            
            # Se estiver em modo edição, usar os valores do contrato
            if self.modo_edicao and self.contrato:
                if len(self.contrato) > 6 and self.contrato[6]:
                    ta_valor = self.contrato[6]
                if len(self.contrato) > 9 and self.contrato[9]:
                    resultado_valor = self.contrato[9]
                if len(self.contrato) > 7 and self.contrato[7]:
                    pta_valor = self.contrato[7]
                if len(self.contrato) > 8 and self.contrato[8]:
                    acao_valor = self.contrato[8]
                if len(self.contrato) > 10 and self.contrato[10]:
                    meta_valor = self.contrato[10]
                if len(self.contrato) > 5 and self.contrato[5]:
                    subprojeto_valor = self.contrato[5]
            
            if instituicao == "FIOCRUZ":
                # FIOCRUZ: Manter apenas Instituição, Instrumento e Subprojeto habilitados
                subprojeto_widget.configure(state="readonly")  # Habilitado (3ª posição)
                
                # Em modo de edição, manter os campos habilitados para visualização
                if self.modo_edicao:
                    ta_widget.configure(state="readonly")
                    resultado_widget.configure(state="readonly")
                    pta_widget.configure(state="readonly")
                    acao_widget.configure(state="readonly")
                    meta_widget.configure(state="readonly")
                else:
                    ta_widget.configure(state="disabled")
                    resultado_widget.configure(state="disabled")
                    pta_widget.configure(state="disabled")
                    acao_widget.configure(state="disabled")
                    meta_widget.configure(state="disabled")  # Meta desabilitado para FIOCRUZ
                
                # Limpar campos desabilitados apenas se não for modo edição
                if not self.modo_edicao:
                    ta_widget.set("")
                    resultado_widget.set("")
                    pta_widget.set("")
                    acao_widget.set("")
                    meta_widget.set("")  # Limpar Meta quando desabilitado
                else:
                    # Restaurar valores originais para modo edição
                    ta_widget.set(ta_valor)
                    resultado_widget.set(resultado_valor)
                    pta_widget.set(pta_valor)
                    acao_widget.set(acao_valor)
                    meta_widget.set(meta_valor)
                
            elif instituicao == "OPAS":
                # OPAS: Desabilitar apenas o campo Subprojeto, Meta habilitado com lista fixa
                # Em modo de edição, manter o campo habilitado para visualização
                if self.modo_edicao:
                    subprojeto_widget.configure(state="readonly")
                else:
                    subprojeto_widget.configure(state="disabled")  # Desabilitado
                
                ta_widget.configure(state="readonly")
                resultado_widget.configure(state="readonly")
                pta_widget.configure(state="readonly")
                acao_widget.configure(state="readonly")
                meta_widget.configure(state="readonly")  # Meta habilitado com lista fixa
                
                # Limpar campo desabilitado apenas se não for modo edição
                if not self.modo_edicao:
                    subprojeto_widget.set("")
                else:
                    # Restaurar valor original para modo edição
                    subprojeto_widget.set(subprojeto_valor)
                
            else:
                # Outras instituições: Habilitar todos os campos, Meta com lista fixa
                subprojeto_widget.configure(state="readonly")
                ta_widget.configure(state="readonly")
                resultado_widget.configure(state="readonly")
                pta_widget.configure(state="readonly")
                acao_widget.configure(state="readonly")
                meta_widget.configure(state="readonly")  # Meta habilitado com lista fixa
                
            # Se estiver em modo edição, garantir que os valores sejam definidos corretamente
            if self.modo_edicao:
                ta_widget.set(ta_valor)
                resultado_widget.set(resultado_valor)
                pta_widget.set(pta_valor)
                acao_widget.set(acao_valor)
                meta_widget.set(meta_valor)
                subprojeto_widget.set(subprojeto_valor)
                
        except Exception as e:
            print(f"Erro ao aplicar regras da instituição: {e}")

    def on_instituicao_changed(self, event=None):
        """Atualizar opções quando a instituição for alterada"""
        try:
            instituicao_selecionada = self.form_custeio.campos["instituicao"]["widget"].get()
            
            # Aplicar regras específicas por instituição
            self.aplicar_regras_instituicao(instituicao_selecionada)
            
            # Atualizar projetos baseado na instituição
            projetos = self.custeio_controller.get_projects(instituicao_selecionada)
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 4 and self.contrato[4]:
                if self.contrato[4] not in projetos:
                    projetos.append(self.contrato[4])
            
            instrumento_widget = self.form_custeio.campos["instrumento"]["widget"]
            instrumento_atual = instrumento_widget.get()
            instrumento_widget["values"] = projetos
            
            # Manter o valor atual se estiver nas opções
            if instrumento_atual in projetos:
                instrumento_widget.set(instrumento_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 4:
                instrumento_widget.set(self.contrato[4])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                instrumento_widget.set("")
            
            # Atualizar campos dependentes
            self.atualizar_campos_dependentes_instrumento()
            
            # Se estiver em modo edição, forçar valores do contrato novamente
            if self.modo_edicao and self.contrato:
                self.form_custeio.master.after(100, self.forcar_valores_contrato)
            
        except Exception as e:
            print(f"Erro ao atualizar projetos: {e}")

    def atualizar_campos_dependentes_instrumento(self):
        """Atualizar campos que dependem de instrumento"""
        try:
            instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
            instrumento = self.form_custeio.campos["instrumento"]["widget"].get()
            
            # Atualizar subprojetos
            subprojetos = []
            if instituicao and instrumento:
                subprojetos = self.custeio_controller.get_subprojects(instituicao, instrumento)
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 5 and self.contrato[5]:
                if self.contrato[5] not in subprojetos:
                    subprojetos.append(self.contrato[5])
            
            subprojeto_widget = self.form_custeio.campos["subprojeto"]["widget"]
            subprojeto_atual = subprojeto_widget.get()
            subprojeto_widget["values"] = subprojetos
            
            # Manter o valor atual se estiver nas opções
            if subprojeto_atual in subprojetos:
                subprojeto_widget.set(subprojeto_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 5:
                subprojeto_widget.set(self.contrato[5])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                subprojeto_widget.set("")
            
            # Atualizar TAs
            tas = []
            if instituicao and instrumento and (instituicao == "OPAS" or instituicao not in ["FIOCRUZ"]):
                tas = self.custeio_controller.get_tas(instituicao, instrumento)
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 6 and self.contrato[6]:
                if self.contrato[6] not in tas:
                    tas.append(self.contrato[6])
            
            ta_widget = self.form_custeio.campos["ta"]["widget"]
            ta_atual = ta_widget.get()
            ta_widget["values"] = tas
            
            # Manter o valor atual se estiver nas opções
            if ta_atual in tas:
                ta_widget.set(ta_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 6:
                ta_widget.set(self.contrato[6])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                ta_widget.set("")
            
            # Atualizar resultados
            resultados = []
            if instituicao and instrumento and ta_widget.get() and (instituicao == "OPAS" or instituicao not in ["FIOCRUZ"]):
                resultados = self.custeio_controller.get_results(instituicao, instrumento, ta_widget.get())
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 9 and self.contrato[9]:
                if self.contrato[9] not in resultados:
                    resultados.append(self.contrato[9])
            
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            resultado_atual = resultado_widget.get()
            resultado_widget["values"] = resultados
            
            # Manter o valor atual se estiver nas opções
            if resultado_atual in resultados:
                resultado_widget.set(resultado_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 9:
                resultado_widget.set(self.contrato[9])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                resultado_widget.set("")
            
            # Para FIOCRUZ, limpar Meta pois fica desabilitado
            # Para outras instituições, Meta mantém lista fixa de 01 a 35
            if instituicao == "FIOCRUZ" and not self.modo_edicao:
                self.form_custeio.campos["meta"]["widget"].set("")
            elif self.modo_edicao and self.contrato and len(self.contrato) > 10:
                # Garantir que o valor da meta seja mantido em modo edição
                self.form_custeio.campos["meta"]["widget"].set(self.contrato[10])
            
        except Exception as e:
            print(f"Erro ao atualizar campos dependentes: {e}")

    def on_instrumento_changed(self, event=None):
        """Atualizar opções quando o instrumento/projeto for alterado"""
        try:
            self.atualizar_campos_dependentes_instrumento()
            
        except Exception as e:
            print(f"Erro ao atualizar subprojetos: {e}")

    def on_subprojeto_changed(self, event=None):
        """Atualizar opções quando o subprojeto for alterado"""
        try:
            instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
            instrumento = self.form_custeio.campos["instrumento"]["widget"].get()
            
            # Para FIOCRUZ, subprojeto é o último campo ativo
            if instituicao == "FIOCRUZ":
                return
            
            # Para OPAS, subprojeto está desabilitado, então não faz nada aqui
            if instituicao == "OPAS":
                return
                
            # Para outras instituições, atualizar TAs baseado em instituição e projeto
            tas = self.custeio_controller.get_tas(instituicao, instrumento)
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 6 and self.contrato[6]:
                if self.contrato[6] not in tas:
                    tas.append(self.contrato[6])
            
            ta_widget = self.form_custeio.campos["ta"]["widget"]
            ta_atual = ta_widget.get()
            ta_widget["values"] = tas
            
            # Manter o valor atual se estiver nas opções
            if ta_atual in tas:
                ta_widget.set(ta_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 6:
                ta_widget.set(self.contrato[6])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                ta_widget.set("")
            
            # Atualizar resultados
            resultados = []
            if instituicao and instrumento and ta_widget.get() and (instituicao == "OPAS" or instituicao not in ["FIOCRUZ"]):
                resultados = self.custeio_controller.get_results(instituicao, instrumento, ta_widget.get())
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 9 and self.contrato[9]:
                if self.contrato[9] not in resultados:
                    resultados.append(self.contrato[9])
            
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            resultado_atual = resultado_widget.get()
            resultado_widget["values"] = resultados
            
            # Manter o valor atual se estiver nas opções
            if resultado_atual in resultados:
                resultado_widget.set(resultado_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 9:
                resultado_widget.set(self.contrato[9])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                resultado_widget.set("")
            
        except Exception as e:
            print(f"Erro ao atualizar TAs: {e}")

    def on_ta_changed(self, event=None):
        """Atualizar opções quando o TA for alterado"""
        try:
            instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
            
            # FIOCRUZ não usa TA, então não faz nada
            if instituicao == "FIOCRUZ":
                return
                
            instrumento = self.form_custeio.campos["instrumento"]["widget"].get()
            ta = self.form_custeio.campos["ta"]["widget"].get()
            
            # Atualizar resultados baseado na instituição, projeto e TA
            resultados = self.custeio_controller.get_results(instituicao, instrumento, ta)
            
            # Se for modo edição, garantir que o valor original esteja nas opções
            if self.contrato and len(self.contrato) > 9 and self.contrato[9]:
                if self.contrato[9] not in resultados:
                    resultados.append(self.contrato[9])
            
            resultado_widget = self.form_custeio.campos["resultado"]["widget"]
            resultado_atual = resultado_widget.get()
            resultado_widget["values"] = resultados
            
            # Manter o valor atual se estiver nas opções
            if resultado_atual in resultados:
                resultado_widget.set(resultado_atual)
            # Se for modo edição, usar o valor do contrato
            elif self.modo_edicao and self.contrato and len(self.contrato) > 9:
                resultado_widget.set(self.contrato[9])
            # Caso contrário, limpar
            elif not self.modo_edicao:
                resultado_widget.set("")
                
        except Exception as e:
            print(f"Erro ao atualizar resultados: {e}")

    def on_resultado_changed(self, event=None):
        """Atualizar opções quando o resultado for alterado"""
        try:
            instituicao = self.form_custeio.campos["instituicao"]["widget"].get()
            
            # FIOCRUZ não usa Resultado, então não faz nada
            if instituicao == "FIOCRUZ":
                return
                
            # Meta sempre mantém lista fixa de 01 a 35 (não atualiza mais baseado em filtros)
            
        except Exception as e:
            print(f"Erro ao atualizar meta: {e}")
    
    def on_meta_changed(self, event=None):
        """Meta agora é independente e não sincroniza mais com Subprojeto"""
        try:
            # Meta agora é um campo independente com lista fixa de 01 a 35
            # Não há mais sincronização com subprojeto
            pass
                
        except Exception as e:
            print(f"Erro no campo meta: {e}")
