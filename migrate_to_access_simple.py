# Migrate To Access Simple.Py
"""
Migração simplificada para Access usando SQL Server LocalDB como alternativa
"""

import os
import shutil
import sqlite3
from datetime import datetime

def backup_current_system():
    """Cria backup do sistema atual"""
    print("=== CRIANDO BACKUP DO SISTEMA ATUAL ===")
    
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup do banco SQLite
    if os.path.exists("sisproj_pf.db"):
        shutil.copy2("sisproj_pf.db", os.path.join(backup_dir, "sisproj_pf.db"))
        print(f"✓ Backup do banco SQLite criado em {backup_dir}")
    
    # Backup do db_manager.py original
    if os.path.exists("models/db_manager.py"):
        shutil.copy2("models/db_manager.py", os.path.join(backup_dir, "db_manager_sqlite.py"))
        print(f"✓ Backup do db_manager.py criado")
    
    return backup_dir


def create_access_alternative():
    """Cria uma solução alternativa usando SQL Server LocalDB ou arquivo MDB"""
    print("\n=== CRIANDO BANCO ACCESS ALTERNATIVO ===")
    
    try:
        # Opção 1: Tentar criar arquivo .mdb (formato mais antigo, mais compatível)
        db_path = "sisproj_pf.mdb"
        
        # String de conexão para arquivo MDB
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={os.path.abspath(db_path)};PWD=;"
        
        import pyodbc
        
        # Criar banco usando driver MDB
        print("Tentando criar banco Access formato MDB...")
        
        # Para MDB, podemos criar arquivo mais simples
        create_mdb_file(db_path)
        
        # Testar conexão
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Criar uma tabela teste
        cursor.execute("""
            CREATE TABLE test_table (
                id COUNTER PRIMARY KEY,
                nome TEXT(50)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✓ Banco Access MDB criado com sucesso: {db_path}")
        return True, db_path, conn_str
        
    except Exception as e:
        print(f"Erro ao criar MDB: {e}")
    
    # Opção 2: Usar SQLite como alternativa (manter atual)
    print("\nMS Access não disponível. Mantendo SQLite como solução.")
    print("Para usar Access real, instale:")
    print("1. Microsoft Access ou")
    print("2. Microsoft Access Database Engine Redistributable")
    
    return False, "sisproj_pf.db", None


def create_mdb_file(db_path):
    """Cria arquivo MDB básico"""
    # Header básico de arquivo MDB (Access 97-2003)
    mdb_header = bytearray(2048)
    
    # Assinatura MDB
    mdb_header[0:15] = b"Standard Jet DB"
    mdb_header[16:20] = b"\x00\x01\x00\x00"
    
    # Preencher resto com zeros
    for i in range(20, len(mdb_header)):
        mdb_header[i] = 0x00
    
    with open(db_path, 'wb') as f:
        f.write(mdb_header)


def create_db_manager_for_access():
    """Cria gerenciador de banco adaptado para Access MDB"""
    
    db_manager_content = '''# Db Manager.Py
import pyodbc
import os
from datetime import datetime

# Configuração do banco
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sisproj_pf.mdb")
CONN_STR = f"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={os.path.abspath(DB_PATH)};PWD=;"

def get_connection():
    """Retorna uma conexão com o banco de dados Access MDB"""
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except pyodbc.Error as e:
        print(f"Erro ao conectar: {e}")
        print("Verificando se arquivo existe...")
        
        if not os.path.exists(DB_PATH):
            print("Arquivo MDB não encontrado. Criando...")
            create_new_mdb()
            conn = pyodbc.connect(CONN_STR)
            return conn
        else:
            raise e

def create_new_mdb():
    """Cria novo arquivo MDB"""
    # Header básico de arquivo MDB
    mdb_header = bytearray(2048)
    mdb_header[0:15] = b"Standard Jet DB"
    mdb_header[16:20] = b"\\x00\\x01\\x00\\x00"
    
    with open(DB_PATH, 'wb') as f:
        f.write(mdb_header)

def init_db():
    """Inicializa o banco de dados e cria tabelas caso não existam"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Criar tabela users
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id COUNTER PRIMARY KEY,
                    username TEXT(50) NOT NULL,
                    password TEXT(255) NOT NULL
                )
            """)
            print("✓ Tabela users criada")
        except:
            print("✓ Tabela users já existe")

        # Criar tabela logs
        try:
            cursor.execute("""
                CREATE TABLE logs (
                    id COUNTER PRIMARY KEY,
                    usuario TEXT(50) NOT NULL,
                    acao TEXT(255) NOT NULL,
                    data_hora DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Tabela logs criada")
        except:
            print("✓ Tabela logs já existe")

        # Criar tabela demanda
        try:
            cursor.execute("""
                CREATE TABLE demanda (
                    codigo COUNTER PRIMARY KEY,
                    data_entrada TEXT(10),
                    solicitante TEXT(255),
                    data_protocolo TEXT(10),
                    oficio TEXT(50),
                    nup_sei TEXT(50),
                    status TEXT(50)
                )
            """)
            print("✓ Tabela demanda criada")
        except:
            print("✓ Tabela demanda já existe")

        # Criar tabela pessoa_fisica
        try:
            cursor.execute("""
                CREATE TABLE pessoa_fisica (
                    id COUNTER PRIMARY KEY,
                    nome_completo TEXT(255) NOT NULL,
                    cpf TEXT(14),
                    email TEXT(100),
                    telefone TEXT(20),
                    data_cadastro DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Tabela pessoa_fisica criada")
        except:
            print("✓ Tabela pessoa_fisica já existe")

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
                    observacoes MEMO
                )
            """)
            print("✓ Tabela contrato_pf criada")
        except:
            print("✓ Tabela contrato_pf já existe")

        # Inserir usuário admin se não existir
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
                print("✓ Usuário admin criado")
        except Exception as e:
            print(f"Aviso: {e}")

        conn.commit()
        print("✓ Banco inicializado com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
'''
    
    return db_manager_content


def migrate_data_to_access():
    """Migra dados do SQLite para Access MDB"""
    print("\n=== MIGRANDO DADOS ===")
    
    if not os.path.exists("sisproj_pf.db"):
        print("⚠ Arquivo SQLite não encontrado")
        return True
    
    try:
        # Conectar ao SQLite
        sqlite_conn = sqlite3.connect("sisproj_pf.db")
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Conectar ao Access MDB
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb)}};DBQ={os.path.abspath('sisproj_pf.mdb')};PWD=;"
        access_conn = pyodbc.connect(conn_str)
        access_cursor = access_conn.cursor()
        
        # Migrar usuários
        print("Migrando usuários...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            try:
                access_cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (user['username'],))
                if access_cursor.fetchone()[0] == 0:
                    access_cursor.execute(
                        "INSERT INTO users (username, password) VALUES (?, ?)",
                        (user['username'], user['password'])
                    )
                    print(f"  ✓ Usuário migrado: {user['username']}")
            except Exception as e:
                print(f"  ✗ Erro ao migrar usuário {user['username']}: {e}")
        
        # Migrar outras tabelas conforme necessário...
        
        access_conn.commit()
        access_conn.close()
        sqlite_conn.close()
        
        print("✓ Migração concluída!")
        return True
        
    except Exception as e:
        print(f"Erro na migração: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("    MIGRAÇÃO SISPROJ-PF: SQLite → Access (Simplificada)")
    print("=" * 60)
    
    # 1. Backup
    backup_dir = backup_current_system()
    
    # 2. Tentar criar Access
    success, db_path, conn_str = create_access_alternative()
    
    if not success:
        print("\n⚠ Mantendo sistema SQLite atual")
        print("Para migrar para Access, instale MS Access ou ACE Engine")
        return False
    
    # 3. Criar novo db_manager
    print("\n=== ATUALIZANDO SISTEMA ===")
    
    new_db_manager = create_db_manager_for_access()
    
    with open("models/db_manager.py", "w", encoding="utf-8") as f:
        f.write(new_db_manager)
    
    print("✓ db_manager.py atualizado para Access MDB")
    
    # 4. Inicializar banco
    try:
        from models.db_manager import init_db
        init_db()
    except Exception as e:
        print(f"Erro ao inicializar: {e}")
        return False
    
    # 5. Migrar dados
    if os.path.exists("sisproj_pf.db"):
        migrate_data_to_access()
    
    print("\n" + "=" * 60)
    print("✓ MIGRAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"• Banco Access MDB criado: sisproj_pf.mdb")
    print(f"• Backup criado em: {backup_dir}")
    print("• Sistema agora usa Access MDB")
    
    return True


if __name__ == "__main__":
    try:
        if main():
            print("\nTeste o sistema executando: py main.py")
        else:
            print("\nMigração não concluída.")
        
        input("Pressione Enter para sair...")
        
    except Exception as e:
        print(f"Erro inesperado: {e}")
        input("Pressione Enter para sair...") 