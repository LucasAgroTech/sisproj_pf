# Db Manager Access.Py
import pyodbc
import os
from datetime import datetime

# Caminho para o banco Access
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sisproj_pf.accdb")


def get_connection():
    """Retorna uma conexão com o banco de dados Access"""
    # String de conexão para Access usando ODBC
    conn_str = (
        f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
        f"DBQ={DB_PATH};"
        f"PWD=;"
    )
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        # Tenta usar driver alternativo se o primeiro falhar
        try:
            conn_str_alt = (
                f"Provider=Microsoft.ACE.OLEDB.12.0;"
                f"Data Source={DB_PATH};"
                f"Persist Security Info=False;"
            )
            import pypyodbc
            conn = pypyodbc.connect(f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_PATH};")
            return conn
        except Exception as e2:
            raise Exception(f"Erro ao conectar com Access: {e}. Erro alternativo: {e2}")


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
        # Verificar se as tabelas já existem
        existing_tables = []
        cursor.execute("SELECT Name FROM MSysObjects WHERE Type=1 AND Flags=0")
        for row in cursor.fetchall():
            existing_tables.append(row[0].lower())

        # Criar tabela users se não existir
        if 'users' not in existing_tables:
            cursor.execute("""
                CREATE TABLE users (
                    id AUTOINCREMENT PRIMARY KEY,
                    username TEXT(50) NOT NULL,
                    password TEXT(255) NOT NULL
                )
            """)
            
            # Criar índice único para username
            cursor.execute("CREATE UNIQUE INDEX idx_users_username ON users (username)")
            
            # Inserir usuário admin padrão
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))

        # Criar tabela logs se não existir
        if 'logs' not in existing_tables:
            cursor.execute("""
                CREATE TABLE logs (
                    id AUTOINCREMENT PRIMARY KEY,
                    usuario TEXT(50) NOT NULL,
                    acao TEXT(255) NOT NULL,
                    data_hora DATETIME DEFAULT NOW()
                )
            """)

        # Criar tabela demanda se não existir
        if 'demanda' not in existing_tables:
            cursor.execute("""
                CREATE TABLE demanda (
                    codigo AUTOINCREMENT PRIMARY KEY,
                    data_entrada TEXT(10),
                    solicitante TEXT(255),
                    data_protocolo TEXT(10),
                    oficio TEXT(50),
                    nup_sei TEXT(50),
                    status TEXT(50)
                )
            """)

        # Criar tabela pessoa_fisica se não existir
        if 'pessoa_fisica' not in existing_tables:
            cursor.execute("""
                CREATE TABLE pessoa_fisica (
                    id AUTOINCREMENT PRIMARY KEY,
                    nome_completo TEXT(255) NOT NULL,
                    cpf TEXT(14),
                    email TEXT(100),
                    telefone TEXT(20),
                    data_cadastro DATETIME DEFAULT NOW()
                )
            """)
            
            # Criar índice único para CPF
            cursor.execute("CREATE UNIQUE INDEX idx_pessoa_fisica_cpf ON pessoa_fisica (cpf)")

        # Criar tabela contrato_pf se não existir
        if 'contrato_pf' not in existing_tables:
            cursor.execute("""
                CREATE TABLE contrato_pf (
                    id AUTOINCREMENT PRIMARY KEY,
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
                    observacoes MEMO
                )
            """)

        # Criar tabela aditivo_pf se não existir  
        if 'aditivo_pf' not in existing_tables:
            cursor.execute("""
                CREATE TABLE aditivo_pf (
                    id AUTOINCREMENT PRIMARY KEY,
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
                    data_atualizacao DATETIME DEFAULT NOW()
                )
            """)

        # Criar tabela produto_pf se não existir
        if 'produto_pf' not in existing_tables:
            cursor.execute("""
                CREATE TABLE produto_pf (
                    id AUTOINCREMENT PRIMARY KEY,
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

        # Criar tabela custeio se não existir
        if 'custeio' not in existing_tables:
            cursor.execute("""
                CREATE TABLE custeio (
                    id AUTOINCREMENT PRIMARY KEY,
                    instituicao_parceira TEXT(255),
                    cod_projeto TEXT(50),
                    cod_ta TEXT(50),
                    resultado TEXT(255),
                    subprojeto TEXT(255),
                    created_at DATETIME DEFAULT NOW()
                )
            """)

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


if __name__ == "__main__":
    # Inicializar banco Access
    init_db()
    
    # Migrar dados do SQLite se existir
    if os.path.exists("sisproj_pf.db"):
        migrate_from_sqlite() 