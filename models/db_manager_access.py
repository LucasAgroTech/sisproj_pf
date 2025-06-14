# Db Manager Access.Py
import pyodbc
import os
from datetime import datetime

# Caminho para o banco Access
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sisproj_pf.accdb"))


def get_connection():
    """Retorna uma conexão com o banco de dados Access"""
    # Tenta primeiro com ACE OLEDB
    conn_str = (
        f"Provider=Microsoft.ACE.OLEDB.12.0;"
        f"Data Source={DB_PATH};"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        # Se falhar, tenta com o driver ODBC
        try:
            conn_str = (
                f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
                f"DBQ={DB_PATH};"
            )
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as e2:
            # Se ambos falharem, tenta com pypyodbc
            try:
                import pypyodbc
                conn = pypyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_PATH};")
                return conn
            except Exception as e3:
                raise Exception(f"Erro ao conectar com Access. Tentativas:\n1) ACE OLEDB: {e}\n2) ODBC: {e2}\n3) pypyodbc: {e3}")


def execute_query(query, params=None):
    """Executa uma query no banco Access"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Se for SELECT, retorna os resultados
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            # Converte para lista de dicionários
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in result]
        else:
            # Para INSERT, UPDATE, DELETE
            conn.commit()
            return cursor.rowcount
            
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_db():
    """Inicializa o banco de dados Access e cria tabelas caso não existam"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Criar tabelas - se já existirem, o erro será ignorado
        
        # Criar tabela users
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id COUNTER PRIMARY KEY,
                    username TEXT(50),
                    password TEXT(255)
                )
            """)
            
            # Criar índice único para username
            cursor.execute("CREATE UNIQUE INDEX idx_users_username ON users (username)")
            
            # Inserir usuário admin padrão
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
            print("Tabela users criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela users: {e}")
                raise e
            print("Tabela users já existe.")

        # Criar tabela logs
        try:
            cursor.execute("""
                CREATE TABLE logs (
                    id COUNTER PRIMARY KEY,
                    usuario TEXT(50),
                    acao TEXT(255),
                    data_hora DATETIME
                )
            """)
            print("Tabela logs criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela logs: {e}")
                raise e
            print("Tabela logs já existe.")

        # Criar tabela demanda
        try:
            cursor.execute("""
                CREATE TABLE demanda (
                    codigo COUNTER PRIMARY KEY,
                    data_entrada TEXT(10),
                    solicitante TEXT(255),
                    data_protocolo TEXT(10),
                    oficio TEXT(50),
                    nup_sei TEXT(50)
                )
            """)
            print("Tabela demanda criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela demanda: {e}")
                raise e
            print("Tabela demanda já existe.")

        # Criar tabela pessoa_fisica
        try:
            cursor.execute("""
                CREATE TABLE pessoa_fisica (
                    id COUNTER PRIMARY KEY,
                    nome_completo TEXT(255),
                    cpf TEXT(14),
                    email TEXT(100),
                    telefone TEXT(20),
                    data_cadastro DATETIME
                )
            """)
            
            # Criar índice único para CPF
            cursor.execute("CREATE UNIQUE INDEX idx_pessoa_fisica_cpf ON pessoa_fisica (cpf)")
            print("Tabela pessoa_fisica criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela pessoa_fisica: {e}")
                raise e
            print("Tabela pessoa_fisica já existe.")

        # Criar tabela contrato_pf
        try:
            cursor.execute("""
                CREATE TABLE contrato_pf (
                    id COUNTER PRIMARY KEY,
                    codigo_demanda LONG,
                    id_pessoa_fisica LONG,
                    instituicao TEXT(255),
                    instrumento TEXT(255),
                    subprojeto TEXT(255),
                    ta TEXT(100),
                    pta TEXT(100),
                    acao TEXT(255),
                    resultado TEXT(255),
                    meta TEXT(255),
                    modalidade TEXT(20),
                    natureza_demanda TEXT(20),
                    numero_contrato TEXT(50),
                    vigencia_inicial TEXT(10),
                    vigencia_final TEXT(10),
                    meses LONG,
                    status_contrato TEXT(50),
                    remuneracao CURRENCY,
                    intersticio INTEGER,
                    valor_intersticio CURRENCY,
                    valor_complementar CURRENCY,
                    total_contrato CURRENCY,
                    observacoes MEMO,
                    lotacao TEXT(255),
                    exercicio TEXT(50)
                )
            """)
            print("Tabela contrato_pf criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela contrato_pf: {e}")
                raise e
            print("Tabela contrato_pf já existe.")

        # Criar tabela aditivo_pf
        try:
            cursor.execute("""
                CREATE TABLE aditivo_pf (
                    id COUNTER PRIMARY KEY,
                    id_contrato LONG,
                    tipo_aditivo TEXT(50),
                    oficio TEXT(50),
                    data_entrada TEXT(10),
                    data_protocolo TEXT(10),
                    instituicao TEXT(255),
                    instrumento TEXT(255),
                    subprojeto TEXT(255),
                    ta TEXT(100),
                    pta TEXT(100),
                    acao TEXT(255),
                    resultado TEXT(255),
                    meta TEXT(255),
                    vigencia_final TEXT(10),
                    meses LONG,
                    valor_aditivo CURRENCY,
                    vigencia_inicial TEXT(10),
                    nova_remuneracao CURRENCY,
                    diferenca_remuneracao CURRENCY,
                    valor_complementar CURRENCY,
                    valor_total_aditivo CURRENCY,
                    responsavel TEXT(100),
                    data_atualizacao DATETIME
                )
            """)
            print("Tabela aditivo_pf criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela aditivo_pf: {e}")
                raise e
            print("Tabela aditivo_pf já existe.")

        # Criar tabela produto_pf
        try:
            cursor.execute("""
                CREATE TABLE produto_pf (
                    id COUNTER PRIMARY KEY,
                    id_contrato LONG,
                    numero TEXT(20),
                    data_programada TEXT(10),
                    instrumento TEXT(255),
                    data_entrega TEXT(10),
                    status TEXT(20),
                    titulo TEXT(255),
                    valor CURRENCY
                )
            """)
            print("Tabela produto_pf criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela produto_pf: {e}")
                raise e
            print("Tabela produto_pf já existe.")

        # Criar tabela custeio
        try:
            cursor.execute("""
                CREATE TABLE custeio (
                    id COUNTER PRIMARY KEY,
                    instituicao_parceira TEXT(255),
                    cod_projeto TEXT(50),
                    cod_ta TEXT(50),
                    resultado TEXT(255),
                    subprojeto TEXT(255),
                    created_at DATETIME
                )
            """)
            print("Tabela custeio criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela custeio: {e}")
                raise e
            print("Tabela custeio já existe.")

        # Criar tabela lists
        try:
            cursor.execute("""
                CREATE TABLE lists (
                    id COUNTER PRIMARY KEY,
                    exercicio TEXT(50),
                    lotacao TEXT(255),
                    solicitante TEXT(255),
                    modalidade_contrato TEXT(50),
                    natureza_demanda TEXT(50),
                    status_contrato TEXT(50)
                )
            """)
            print("Tabela lists criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela lists: {e}")
                raise e
            print("Tabela lists já existe.")

        # Criar tabela modalidade_contrato
        try:
            cursor.execute("""
                CREATE TABLE modalidade_contrato (
                    id COUNTER PRIMARY KEY,
                    modalidade TEXT(50)
                )
            """)
            print("Tabela modalidade_contrato criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela modalidade_contrato: {e}")
                raise e
            print("Tabela modalidade_contrato já existe.")

        # Criar tabela natureza_demanda
        try:
            cursor.execute("""
                CREATE TABLE natureza_demanda (
                    id COUNTER PRIMARY KEY,
                    natureza TEXT(50)
                )
            """)
            print("Tabela natureza_demanda criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela natureza_demanda: {e}")
                raise e
            print("Tabela natureza_demanda já existe.")

        # Criar tabela status_contrato
        try:
            cursor.execute("""
                CREATE TABLE status_contrato (
                    id COUNTER PRIMARY KEY,
                    status TEXT(50)
                )
            """)
            print("Tabela status_contrato criada com sucesso!")
        except Exception as e:
            if "já existe" not in str(e):
                print(f"Erro ao criar tabela status_contrato: {e}")
                raise e
            print("Tabela status_contrato já existe.")

        conn.commit()
        print("Banco de dados Access inicializado com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inicializar banco Access: {e}")
        raise e
    finally:
        conn.close()


def migrate_from_sqlite():
    """Migra dados do SQLite para Access"""
    import sqlite3
    
    # Conectar ao SQLite
    sqlite_conn = sqlite3.connect("sisproj_pf.db")  
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar ao Access
    access_conn = get_connection()
    access_cursor = access_conn.cursor()
    
    try:
        # Tabelas a serem migradas
        tables = [
            'users', 'logs', 'demanda', 'pessoa_fisica', 
            'contrato_pf', 'aditivo_pf', 'produto_pf', 'custeio'
        ]
        
        for table in tables:
            print(f"Migrando tabela {table}...")
            
            try:
                # Buscar dados do SQLite
                sqlite_cursor.execute(f"SELECT * FROM {table}")
                rows = sqlite_cursor.fetchall()
                
                if not rows:
                    print(f"  - Tabela {table} vazia, pulando...")
                    continue
                
                # Obter nomes das colunas
                columns = [description[0] for description in sqlite_cursor.description]
                
                # Limpar tabela Access antes de inserir (exceto users se já tiver admin)
                if table == 'users':
                    access_cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
                    admin_exists = access_cursor.fetchone()[0] > 0
                    if not admin_exists:
                        access_cursor.execute(f"DELETE FROM {table}")
                else:
                    access_cursor.execute(f"DELETE FROM {table}")
                
                # Preparar query de inserção
                placeholders = ', '.join(['?' for _ in columns])
                insert_query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                
                # Inserir dados
                for row in rows:
                    # Pular usuário admin se já existir no Access
                    if table == 'users' and row['username'] == 'admin' and admin_exists:
                        continue
                        
                    # Converter dados para formato Access
                    row_data = []
                    for i, value in enumerate(row):
                        if value is None:
                            row_data.append(None)
                        elif columns[i] in ['data_cadastro', 'data_hora', 'data_atualizacao', 'created_at']:
                            # Tratar campos de data/hora
                            if isinstance(value, str) and value.strip():
                                try:
                                    row_data.append(datetime.fromisoformat(value.replace('Z', '')))
                                except:
                                    row_data.append(value)
                            else:
                                row_data.append(None)
                        else:
                            row_data.append(value)
                    
                    access_cursor.execute(insert_query, row_data)
                
                print(f"  - {len(rows)} registros migrados para {table}")
                
            except Exception as e:
                print(f"  - Erro ao migrar tabela {table}: {e}")
                continue
        
        access_conn.commit()
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        access_conn.rollback()
        print(f"Erro durante migração: {e}")
        raise e
    finally:
        sqlite_conn.close()
        access_conn.close()


def get_lists_data():
    """Retorna os dados das tabelas de listas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("Buscando dados da tabela lists...")
        
        # Buscar todos os dados da tabela lists
        cursor.execute("SELECT exercicio, lotacao, solicitante, modalidade_contrato, natureza_demanda, status_contrato FROM lists")
        lists_result = cursor.fetchall()
        print(f"Dados da tabela lists: {lists_result}")
        
        # Organizar os dados em listas únicas
        exercicios = sorted(list(set(row[0] for row in lists_result if row[0])))
        lotacoes = sorted(list(set(row[1] for row in lists_result if row[1])))
        solicitantes = sorted(list(set(row[2] for row in lists_result if row[2])))
        modalidades = sorted(list(set(row[3] for row in lists_result if row[3])))
        naturezas = sorted(list(set(row[4] for row in lists_result if row[4])))
        status = sorted(list(set(row[5] for row in lists_result if row[5])))
        
        return {
            'exercicios': exercicios,
            'lotacoes': lotacoes,
            'solicitantes': solicitantes,
            'modalidades': modalidades,
            'naturezas': naturezas,
            'status': status
        }
    except Exception as e:
        print(f"Erro ao buscar dados da tabela lists: {e}")
        # Se houver erro, retornar valores padrão
        return {
            'exercicios': [], 
            'lotacoes': [], 
            'solicitantes': [],
            'modalidades': ["BOLSA", "PRODUTO", "RPA", "CLT"],  # valores padrão
            'naturezas': ["NOVO", "RENOVAÇÃO"],  # valores padrão
            'status': ["VIGENTE", "PENDENTE_ASSINATURA", "CANCELADO", "CONCLUIDO", "EM_TRAMITACAO", "AGUARDANDO_AUTORIZACAO", "NAO_AUTORIZADO", "RESCINDIDO"]  # valores padrão
        }
    finally:
        conn.close()


def validate_list_value(cursor, column_name, value):
    """Valida se um valor existe na coluna especificada da tabela lists"""
    if value is None:
        return True
        
    cursor.execute(f"SELECT COUNT(*) FROM lists WHERE {column_name} = ?", (value,))
    count = cursor.fetchone()[0]
    return count > 0


if __name__ == "__main__":
    # Inicializar banco Access
    init_db()
    
    # Migrar dados do SQLite se existir
    if os.path.exists("sisproj_pf.db"):
        migrate_from_sqlite() 