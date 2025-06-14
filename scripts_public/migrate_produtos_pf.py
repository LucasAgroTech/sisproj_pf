#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de Migração de Produtos PF da Planilha para o Banco SQLite
==================================================================

Este script migra dados da aba Produto_PF da planilha dados_migrar.xlsx 
para a tabela produto_pf do banco sisproj_pf.db, mantendo as outras 
tabelas intactas e garantindo a integridade referencial com os contratos.

IMPORTANTE: Este script NÃO apaga as outras tabelas (pessoa_fisica, 
demanda, contrato_pf), apenas limpa e migra a tabela produto_pf.

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
        backup_name = f"backup_produtos_pf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.system(f'copy "sisproj_pf.db" "{backup_name}"')
        log_message(f"Backup criado: {backup_name}")
        return backup_name
    return None


def clean_produtos_table():
    """Limpa apenas a tabela produto_pf mantendo a estrutura"""
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    try:
        log_message("Limpando apenas a tabela produto_pf...")
        
        # Desabilitar chaves estrangeiras temporariamente
        cursor.execute("PRAGMA foreign_keys = OFF")
        
        # Limpar apenas produtos
        cursor.execute("DELETE FROM produto_pf")
        log_message("Tabela produto_pf limpa")
        
        # Reset do ID auto-incremental
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'produto_pf'")
        
        # Reabilitar chaves estrangeiras
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        log_message("Limpeza da tabela produto_pf concluída!")
        
    except Exception as e:
        log_message(f"Erro durante limpeza: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def normalize_status_produto(status):
    """Normaliza o status do produto para valores aceitos pelo constraint"""
    if pd.isna(status) or str(status).strip() == '':
        return 'programado'  # Status padrão
    
    status_str = str(status).strip().lower()
    
    # Mapeamento de status para o formato original do sistema
    status_map = {
        # Variações de "programado"
        'programado': 'programado',
        'programada': 'programado',
        'pendente': 'programado',
        'agendado': 'programado',
        'planejado': 'programado',
        
        # Variações de "em execução"
        'em execução': 'em_execucao',
        'em execucao': 'em_execucao',
        'em_execucao': 'em_execucao',
        'executando': 'em_execucao',
        'andamento': 'em_execucao',
        'em andamento': 'em_execucao',
        
        # Variações de "entregue"
        'entregue': 'entregue',
        'entregues': 'entregue',
        'finalizado': 'entregue',
        'concluido': 'entregue',
        'concluído': 'entregue',
        'completo': 'entregue',
        'terminado': 'entregue',
        
        # Variações de "cancelado"
        'cancelado': 'cancelado',
        'cancelada': 'cancelado',
        'suspenso': 'cancelado',
        'interrompido': 'cancelado',
        'anulado': 'cancelado'
    }
    
    return status_map.get(status_str, 'programado')


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


def generate_numero_produto(index, id_contrato):
    """Gera um número sequencial para o produto baseado no índice e contrato"""
    return f"PROD-{id_contrato}-{index:04d}"


def migrate_produtos_pf():
    """Migra dados da aba Produto_PF para a tabela produto_pf"""
    log_message("Iniciando migração de produtos PF...")
    
    # Ler dados da planilha
    df = pd.read_excel('dados_migrar.xlsx', sheet_name='Produto_PF')
    
    # Mapear colunas da planilha para os campos da tabela
    # Colunas da planilha: ['id_contrato', 'data_programada', 'instrumento', 'data_entrega', 'status', 'titulo', 'VALOR DAS PARCELAS']
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    success_count = 0
    error_count = 0
    skipped_count = 0  # Contratos inexistentes
    
    try:
        for index, row in df.iterrows():
            try:
                # Verificar se o contrato existe
                id_contrato = int(row['id_contrato'])
                cursor.execute("SELECT COUNT(*) FROM contrato_pf WHERE id = ?", (id_contrato,))
                if cursor.fetchone()[0] == 0:
                    log_message(f"Linha {index + 2}: Contrato ID {id_contrato} não encontrado, pulando", "WARNING")
                    skipped_count += 1
                    continue
                
                # Preparar dados
                numero = generate_numero_produto(index + 1, id_contrato)
                data_programada = format_date(row['data_programada'])
                instrumento = str(row['instrumento']).strip() if not pd.isna(row['instrumento']) else None
                data_entrega = format_date(row['data_entrega'])
                status = normalize_status_produto(row['status'])
                titulo = str(row['titulo']).strip() if not pd.isna(row['titulo']) else None
                
                # Valor pode estar na coluna 'VALOR DAS PARCELAS'
                valor_raw = row.get('VALOR DAS PARCELAS', 0)
                if pd.isna(valor_raw):
                    valor = 0.0
                else:
                    try:
                        valor = float(valor_raw)
                    except (ValueError, TypeError):
                        valor = 0.0
                
                # Inserir no banco
                cursor.execute("""
                    INSERT INTO produto_pf (
                        id_contrato, numero, data_programada, instrumento, 
                        data_entrega, status, titulo, valor
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id_contrato, numero, data_programada, instrumento,
                    data_entrega, status, titulo, valor
                ))
                
                success_count += 1
                
                # Log a cada 1000 registros processados
                if (index + 1) % 1000 == 0:
                    log_message(f"Processados {index + 1} registros...")
                
            except Exception as e:
                error_count += 1
                log_message(f"Erro na linha {index + 2}: {e}", "ERROR")
        
        conn.commit()
        log_message(f"Migração produtos PF concluída: {success_count} sucessos, {error_count} erros, {skipped_count} pulados")
        
    except Exception as e:
        log_message(f"Erro geral na migração produtos PF: {e}", "ERROR")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_produtos_migration():
    """Verifica a integridade dos produtos migrados"""
    log_message("Verificando integridade dos produtos migrados...")
    
    conn = sqlite3.connect("sisproj_pf.db")
    cursor = conn.cursor()
    
    try:
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM produto_pf")
        count_produtos = cursor.fetchone()[0]
        
        log_message(f"Produtos migrados: {count_produtos}")
        
        # Verificar integridade referencial
        cursor.execute("""
            SELECT COUNT(*) FROM produto_pf p
            LEFT JOIN contrato_pf c ON p.id_contrato = c.id
            WHERE c.id IS NULL
        """)
        orphan_produtos = cursor.fetchone()[0]
        
        if orphan_produtos > 0:
            log_message(f"ATENÇÃO: {orphan_produtos} produtos com contrato inexistente", "WARNING")
        else:
            log_message("Integridade referencial verificada: OK!")
        
        # Estatísticas por status
        cursor.execute("SELECT status, COUNT(*) FROM produto_pf GROUP BY status ORDER BY COUNT(*) DESC")
        log_message("Produtos por status:")
        for status, count in cursor.fetchall():
            log_message(f"  - {status}: {count}")
        
        # Verificar se há produtos com valor
        cursor.execute("SELECT COUNT(*) FROM produto_pf WHERE valor > 0")
        produtos_com_valor = cursor.fetchone()[0]
        log_message(f"Produtos com valor > 0: {produtos_com_valor}")
        
        # Verificar distribuição por modalidade do contrato
        cursor.execute("""
            SELECT c.modalidade, COUNT(p.id) as total_produtos
            FROM contrato_pf c
            LEFT JOIN produto_pf p ON c.id = p.id_contrato
            GROUP BY c.modalidade
            ORDER BY total_produtos DESC
        """)
        log_message("Produtos por modalidade de contrato:")
        for modalidade, count in cursor.fetchall():
            log_message(f"  - {modalidade}: {count} produtos")
        
    except Exception as e:
        log_message(f"Erro na verificação: {e}", "ERROR")
    finally:
        conn.close()


def main():
    """Função principal de migração de produtos"""
    print("=" * 60)
    print("MIGRAÇÃO DE PRODUTOS PF DA PLANILHA PARA O BANCO SQLITE")
    print("=" * 60)
    
    try:
        # Verificar se arquivos existem
        if not os.path.exists("dados_migrar.xlsx"):
            log_message("Arquivo dados_migrar.xlsx não encontrado!", "ERROR")
            return False
        
        if not os.path.exists("sisproj_pf.db"):
            log_message("Banco sisproj_pf.db não encontrado!", "ERROR")
            return False
        
        # Verificar se a aba existe
        try:
            excel_file = pd.ExcelFile('dados_migrar.xlsx')
            if 'Produto_PF' not in excel_file.sheet_names:
                log_message("Aba 'Produto_PF' não encontrada na planilha!", "ERROR")
                return False
        except Exception as e:
            log_message(f"Erro ao acessar a planilha: {e}", "ERROR")
            return False
        
        # Criar backup
        backup_file = backup_database()
        
        # Perguntar confirmação
        response = input("\nEsta operação irá LIMPAR apenas a tabela produto_pf. Continuar? (S/n): ")
        if response.lower() not in ['s', 'sim', 'y', 'yes', '']:
            log_message("Operação cancelada pelo usuário.")
            return False
        
        # Executar migração
        clean_produtos_table()
        migrate_produtos_pf()
        verify_produtos_migration()
        
        print("\n" + "=" * 60)
        log_message("MIGRAÇÃO DE PRODUTOS CONCLUÍDA COM SUCESSO!")
        if backup_file:
            log_message(f"Backup disponível em: {backup_file}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        log_message(f"Erro durante a migração: {e}", "ERROR")
        print("\n" + "=" * 60)
        log_message("MIGRAÇÃO DE PRODUTOS FALHOU!")
        if backup_file:
            log_message(f"Restaure o backup se necessário: {backup_file}")
        print("=" * 60)
        return False


if __name__ == "__main__":
    main() 