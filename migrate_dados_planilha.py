#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Migração de Dados da Planilha para o Banco SQLite
============================================================

Este script migra dados das abas pessoa_fisica, demanda e contrato_pf
da planilha dados_migrar.xlsx para o banco sisproj_pf.db, mantendo
as relações entre os dados e garantindo a integridade referencial.

IMPORTANTE: Os dados da planilha são NORMALIZADOS para o formato 
ORIGINAL do sistema:
- modalidade: MAIÚSCULO ('BOLSA', 'PRODUTO', 'RPA', 'CLT')
- natureza_demanda: minúsculo ('novo', 'renovacao')  
- status_contrato: minúsculo com underscores ('pendente_assinatura', etc.)

Autor: Sistema de Migração Automática
Data: 2025-06-08
"""

import pandas as pd
import sqlite3
import sys
from datetime import datetime
import os


def log_message(message, level="INFO"):
    """Log de mensagens com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def backup_database():
    """Cria backup do banco antes da migração"""
    if os.path.exists("sisproj_pf.db"):
        backup_name = f"backup_sisproj_pf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.system(f'copy "sisproj_pf.db" "{backup_name}"')
        log_message(f"Backup criado: {backup_name}")
        return backup_name
    return None


def clean_database():
    """Limpa os dados das tabelas principais mantendo a estrutura"""
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    try:
        log_message("Iniciando limpeza do banco de dados...")
        
        # Desabilitar chaves estrangeiras temporariamente
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Limpar tabelas na ordem correta (dependências)
        tables_to_clean = [
            'produto_pf',      # Depende de contrato_pf
            'aditivo_pf',      # Depende de contrato_pf  
            'contrato_pf',     # Depende de pessoa_fisica e demanda
            'pessoa_fisica',   # Independente
            'demanda',         # Independente
        ]
        
        for table in tables_to_clean:
            cursor.execute(f"DELETE FROM {table}")
            log_message(f"Tabela {table} limpa")
        
        # Reset dos IDs auto-incrementais
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('pessoa_fisica', 'demanda', 'contrato_pf', 'produto_pf', 'aditivo_pf')")
        
        # Reabilitar chaves estrangeiras
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        log_message("Limpeza do banco concluída com sucesso!")
        
    except Exception as e:
        log_message(f"Erro durante limpeza: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def normalize_status_contrato(status):
    """Normaliza o status do contrato para o formato ORIGINAL do sistema (minúsculo com underscores)"""
    if pd.isna(status):
        return 'pendente_assinatura'
    
    status_str = str(status).strip().lower()
    
    # Mapeamento completo para o formato original do sistema
    status_map = {
        # Variações de "concluído"
        'concluido': 'concluido',
        'concluído': 'concluido',
        'concluida': 'concluido',
        'concluída': 'concluido',
        
        # Variações de "cancelado"
        'cancelado': 'cancelado',
        'cancelada': 'cancelado',
        
        # Variações de "vigente"
        'vigente': 'vigente',
        
        # Variações de "em tramitação"
        'em tramitação': 'em_tramitacao',
        'em tramitacao': 'em_tramitacao',
        'em_tramitacao': 'em_tramitacao',
        'tramitacao': 'em_tramitacao',
        'tramitação': 'em_tramitacao',
        
        # Variações de "pendente assinatura"
        'pendente': 'pendente_assinatura',
        'pendente_assinatura': 'pendente_assinatura',
        'assinatura pendente': 'pendente_assinatura',
        'pendente de assinatura': 'pendente_assinatura',
        
        # Variações de "aguardando autorização"
        'aguardando': 'aguardando_autorizacao',
        'aguardando_autorizacao': 'aguardando_autorizacao',
        'aguardando autorização': 'aguardando_autorizacao',
        'aguardando autorizacao': 'aguardando_autorizacao',
        
        # Variações de "não autorizado"
        'não autorizado': 'nao_autorizado',
        'nao_autorizado': 'nao_autorizado',
        'nao autorizado': 'nao_autorizado',
        'não_autorizado': 'nao_autorizado',
        
        # Variações de "rescindido"
        'rescindido': 'rescindido',
        'rescindida': 'rescindido'
    }
    
    return status_map.get(status_str, 'pendente_assinatura')


def normalize_modalidade(modalidade):
    """Normaliza a modalidade para o formato ORIGINAL do sistema (MAIÚSCULO)"""
    if pd.isna(modalidade):
        return 'PRODUTO'
    
    modalidade_str = str(modalidade).strip().upper()
    
    # Mapeamento completo para o formato original do sistema
    modalidade_map = {
        # Variações de "BOLSA"
        'BOLSA': 'BOLSA',
        'BOLSAS': 'BOLSA',
        'BOLSISTA': 'BOLSA',
        'BOLSISTAS': 'BOLSA',
        
        # Variações de "PRODUTO"
        'PRODUTO': 'PRODUTO',
        'PRODUTOS': 'PRODUTO',
        'PRODUÇÃO': 'PRODUTO',
        'PRODUCAO': 'PRODUTO',
        
        # Variações de "RPA"
        'RPA': 'RPA',
        'RPAS': 'RPA',
        'R.P.A': 'RPA',
        'R.P.A.': 'RPA',
        
        # Variações de "CLT"
        'CLT': 'CLT',
        'CELETISTA': 'CLT',
        'EMPREGADO': 'CLT',
        'FUNCIONARIO': 'CLT',
        'FUNCIONÁRIO': 'CLT'
    }
    
    return modalidade_map.get(modalidade_str, 'PRODUTO')


def normalize_natureza_demanda(natureza):
    """Normaliza a natureza da demanda para o formato ORIGINAL do sistema (minúsculo)"""
    if pd.isna(natureza):
        return 'novo'
    
    natureza_str = str(natureza).strip().lower()
    
    # Mapeamento para o formato original do sistema
    natureza_map = {
        # Variações de "renovação"
        'renovacao': 'renovacao',
        'renovação': 'renovacao',
        'renovacão': 'renovacao',
        'renovaçao': 'renovacao',
        'renov': 'renovacao',
        'renovar': 'renovacao',
        
        # Variações de "novo"
        'novo': 'novo',
        'nova': 'novo',
        'novos': 'novo',
        'novas': 'novo',
        'inicial': 'novo',
        'primeiro': 'novo',
        'primeira': 'novo'
    }
    
    return natureza_map.get(natureza_str, 'novo')


def format_date(date_value):
    """Formata datas para o padrão do banco"""
    if pd.isna(date_value):
        return None
    
    if isinstance(date_value, datetime):
        return date_value.strftime('%Y-%m-%d')
    
    # Tentar converter string para data
    try:
        if isinstance(date_value, str):
            # Remover possível informação de hora
            date_str = date_value.split(' ')[0]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
    except:
        pass
    
    return None


def migrate_pessoa_fisica():
    """Migra dados da tabela pessoa_fisica"""
    log_message("Iniciando migração de pessoa_fisica...")
    
    # Ler dados da planilha
    df = pd.read_excel('dados_migrar.xlsx', sheet_name='pessoa_fisica')
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        for index, row in df.iterrows():
            try:
                # Preparar dados
                nome_completo = str(row['nome_completo']).strip() if not pd.isna(row['nome_completo']) else None
                cpf = str(row['cpf']).strip() if not pd.isna(row['cpf']) else None
                email = str(row['email']).strip() if not pd.isna(row['email']) else None
                telefone = str(row['telefone']).strip() if not pd.isna(row['telefone']) else None
                data_cadastro = format_date(row['data_cadastro']) or datetime.now().strftime('%Y-%m-%d')
                
                if not nome_completo:
                    log_message(f"Linha {index + 2}: Nome completo vazio, pulando", "WARNING")
                    error_count += 1
                    continue
                
                # Inserir no banco usando o ID original da planilha
                cursor.execute("""
                    INSERT INTO pessoa_fisica (id, nome_completo, cpf, email, telefone, data_cadastro)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (int(row['id']), nome_completo, cpf, email, telefone, data_cadastro))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                log_message(f"Erro na linha {index + 2}: {e}", "ERROR")
        
        conn.commit()
        log_message(f"Migração pessoa_fisica concluída: {success_count} sucessos, {error_count} erros")
        
    except Exception as e:
        log_message(f"Erro geral na migração pessoa_fisica: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_demanda():
    """Migra dados da tabela demanda"""
    log_message("Iniciando migração de demanda...")
    
    # Ler dados da planilha
    df = pd.read_excel('dados_migrar.xlsx', sheet_name='demanda')
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        for index, row in df.iterrows():
            try:
                # Preparar dados
                codigo = int(row['codigo'])
                data_entrada = format_date(row['data_entrada'])
                solicitante = str(row['solicitante']).strip() if not pd.isna(row['solicitante']) else None
                data_protocolo = format_date(row['data_protocolo'])
                oficio = str(row['oficio']).strip() if not pd.isna(row['oficio']) else None
                nup_sei = str(row['nup_sei']).strip() if not pd.isna(row['nup_sei']) else None
                status = str(row['status']).strip() if not pd.isna(row['status']) else 'Novo'
                
                # Inserir no banco usando o código original da planilha
                cursor.execute("""
                    INSERT INTO demanda (codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (codigo, data_entrada, solicitante, data_protocolo, oficio, nup_sei, status))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                log_message(f"Erro na linha {index + 2}: {e}", "ERROR")
        
        conn.commit()
        log_message(f"Migração demanda concluída: {success_count} sucessos, {error_count} erros")
        
    except Exception as e:
        log_message(f"Erro geral na migração demanda: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_contrato_pf():
    """Migra dados da tabela contrato_pf"""
    log_message("Iniciando migração de contrato_pf...")
    
    # Ler dados da planilha
    df = pd.read_excel('dados_migrar.xlsx', sheet_name='contrato_pf')
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        for index, row in df.iterrows():
            try:
                # Verificar se pessoa_fisica e demanda existem
                cursor.execute("SELECT COUNT(*) FROM pessoa_fisica WHERE id = ?", (int(row['id_pessoa_fisica']),))
                if cursor.fetchone()[0] == 0:
                    log_message(f"Linha {index + 2}: Pessoa física ID {row['id_pessoa_fisica']} não encontrada", "WARNING")
                    error_count += 1
                    continue
                
                cursor.execute("SELECT COUNT(*) FROM demanda WHERE codigo = ?", (int(row['codigo_demanda']),))
                if cursor.fetchone()[0] == 0:
                    log_message(f"Linha {index + 2}: Demanda código {row['codigo_demanda']} não encontrada", "WARNING")
                    error_count += 1
                    continue
                
                # Preparar dados
                id_contrato = int(row['id'])
                codigo_demanda = int(row['codigo_demanda'])
                id_pessoa_fisica = int(row['id_pessoa_fisica'])
                instituicao = str(row['instituicao']).strip() if not pd.isna(row['instituicao']) else None
                instrumento = str(row['instrumento']).strip() if not pd.isna(row['instrumento']) else None
                subprojeto = str(row['subprojeto']).strip() if not pd.isna(row['subprojeto']) else None
                ta = str(row['ta']).strip() if not pd.isna(row['ta']) else None
                pta = str(row['pta']).strip() if not pd.isna(row['pta']) else None
                acao = str(row['acao']).strip() if not pd.isna(row['acao']) else None
                resultado = str(row['resultado']).strip() if not pd.isna(row['resultado']) else None
                meta = str(row['meta']).strip() if not pd.isna(row['meta']) else None
                modalidade = normalize_modalidade(row['modalidade'])
                natureza_demanda = normalize_natureza_demanda(row['natureza_demanda'])
                numero_contrato = str(row['numero_contrato']).strip() if not pd.isna(row['numero_contrato']) else None
                vigencia_inicial = format_date(row['vigencia_inicial'])
                vigencia_final = format_date(row['vigencia_final'])
                meses = int(row['meses']) if not pd.isna(row['meses']) else 0
                status_contrato = normalize_status_contrato(row['status_contrato'])
                remuneracao = float(row['remuneracao']) if not pd.isna(row['remuneracao']) else 0.0
                intersticio = int(row['intersticio']) if not pd.isna(row['intersticio']) else 0
                valor_intersticio = float(row['valor_intersticio']) if not pd.isna(row['valor_intersticio']) else 0.0
                valor_complementar = float(row['valor_complementar']) if not pd.isna(row['valor_complementar']) else 0.0
                total_contrato = float(row['total_contrato']) if not pd.isna(row['total_contrato']) else 0.0
                observacoes = str(row['observacoes']).strip() if not pd.isna(row['observacoes']) else None
                
                # Inserir no banco
                cursor.execute("""
                    INSERT INTO contrato_pf (
                        id, codigo_demanda, id_pessoa_fisica, instituicao, instrumento, subprojeto,
                        ta, pta, acao, resultado, meta, modalidade, natureza_demanda, numero_contrato,
                        vigencia_inicial, vigencia_final, meses, status_contrato, remuneracao,
                        intersticio, valor_intersticio, valor_complementar, total_contrato, observacoes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_contrato, codigo_demanda, id_pessoa_fisica, instituicao, instrumento, subprojeto,
                    ta, pta, acao, resultado, meta, modalidade, natureza_demanda, numero_contrato,
                    vigencia_inicial, vigencia_final, meses, status_contrato, remuneracao,
                    intersticio, valor_intersticio, valor_complementar, total_contrato, observacoes
                ))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                log_message(f"Erro na linha {index + 2}: {e}", "ERROR")
        
        conn.commit()
        log_message(f"Migração contrato_pf concluída: {success_count} sucessos, {error_count} erros")
        
    except Exception as e:
        log_message(f"Erro geral na migração contrato_pf: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration():
    """Verifica a integridade dos dados migrados"""
    log_message("Verificando integridade dos dados migrados...")
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    try:
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM pessoa_fisica")
        count_pf = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM demanda")
        count_demanda = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM contrato_pf")
        count_contrato = cursor.fetchone()[0]
        
        log_message(f"Registros migrados:")
        log_message(f"  - Pessoas Físicas: {count_pf}")
        log_message(f"  - Demandas: {count_demanda}")
        log_message(f"  - Contratos PF: {count_contrato}")
        
        # Verificar integridade referencial
        cursor.execute("""
            SELECT COUNT(*) FROM contrato_pf c
            LEFT JOIN pessoa_fisica p ON c.id_pessoa_fisica = p.id
            WHERE p.id IS NULL
        """)
        orphan_pf = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM contrato_pf c
            LEFT JOIN demanda d ON c.codigo_demanda = d.codigo
            WHERE d.codigo IS NULL
        """)
        orphan_demanda = cursor.fetchone()[0]
        
        if orphan_pf > 0:
            log_message(f"ATENÇÃO: {orphan_pf} contratos com pessoa_fisica inexistente", "WARNING")
        
        if orphan_demanda > 0:
            log_message(f"ATENÇÃO: {orphan_demanda} contratos com demanda inexistente", "WARNING")
        
        if orphan_pf == 0 and orphan_demanda == 0:
            log_message("Integridade referencial verificada: OK!")
        
    except Exception as e:
        log_message(f"Erro na verificação: {e}", "ERROR")
    finally:
        conn.close()


def main():
    """Função principal de migração"""
    print("=" * 60)
    print("MIGRAÇÃO DE DADOS DA PLANILHA PARA O BANCO SQLITE")
    print("=" * 60)
    
    try:
        # Verificar se arquivos existem
        if not os.path.exists("dados_migrar.xlsx"):
            log_message("Arquivo dados_migrar.xlsx não encontrado!", "ERROR")
            return False
        
        if not os.path.exists("sisproj_pf.db"):
            log_message("Banco sisproj_pf.db não encontrado!", "ERROR")
            return False
        
        # Criar backup
        backup_file = backup_database()
        
        # Perguntar confirmação
        response = input("\nEsta operação irá LIMPAR todos os dados do banco. Continuar? (S/n): ")
        if response.lower() not in ['s', 'sim', 'y', 'yes', '']:
            log_message("Operação cancelada pelo usuário.")
            return False
        
        # Executar migração
        clean_database()
        migrate_pessoa_fisica()
        migrate_demanda()
        migrate_contrato_pf()
        verify_migration()
        
        print("\n" + "=" * 60)
        log_message("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        if backup_file:
            log_message(f"Backup disponível em: {backup_file}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        log_message(f"Erro durante a migração: {e}", "ERROR")
        print("\n" + "=" * 60)
        log_message("MIGRAÇÃO FALHOU!")
        if backup_file:
            log_message(f"Restaure o backup se necessário: {backup_file}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    main() 