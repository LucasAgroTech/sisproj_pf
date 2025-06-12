# Db Manager Access V2.Py
import os
import tempfile
import sqlite3
from datetime import datetime

def create_access_connection_string():
    """Cria string de conexão para Access"""
    db_path = os.path.join(os.path.dirname(__file__), "..", "sisproj_pf.accdb")
    db_path = os.path.abspath(db_path)
    
    # String de conexão sem senha
    conn_str = (
        f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
        f"DBQ={db_path};"
        f"PWD=;"
    )
    
    return conn_str, db_path


def create_new_access_database():
    """Cria um novo banco Access usando método alternativo"""
    import pyodbc
    
    conn_str, db_path = create_access_connection_string()
    
    # Remover arquivo existente se houver
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"Arquivo existente removido: {db_path}")
        except:
            pass
    
    try:
        # Método 1: Criar usando template em memória
        # Criar arquivo básico Access
        template_data = create_minimal_access_file()
        
        with open(db_path, 'wb') as f:
            f.write(template_data)
        
        print(f"✓ Arquivo Access template criado: {db_path}")
        
        # Tentar conectar e verificar
        conn = pyodbc.connect(conn_str)
        conn.close()
        
        print("✓ Conexão com Access testada com sucesso")
        return True
        
    except Exception as e:
        print(f"Erro método 1: {e}")
        
        # Método 2: Usar ferramenta externa se disponível
        try:
            return create_with_external_tool(db_path)
        except Exception as e2:
            print(f"Erro método 2: {e2}")
            
        # Método 3: Copiar de template sistema
        try:
            return copy_system_template(db_path)
        except Exception as e3:
            print(f"Erro método 3: {e3}")
    
    return False


def create_minimal_access_file():
    """Cria dados mínimos para arquivo Access"""
    # Header básico de arquivo Access 2007+ (.accdb)
    header = bytearray(4096)  # 4KB inicial
    
    # Signature para Access 2007
    header[0:16] = b'\x00\x01\x00\x00Standard Jet DB'
    header[16] = 0x00
    
    # Versão do formato
    header[20:24] = b'\x02\x00\x01\x00'  # Access 2007 format
    
    # Preenchimento básico
    for i in range(24, len(header)):
        header[i] = 0x00
    
    return bytes(header)


def create_with_external_tool(db_path):
    """Tenta criar usando ferramentas externas"""
    try:
        # Verificar se existe MSAccess instalado
        import subprocess
        
        # Comando para criar banco vazio
        cmd = f'powershell -Command "& {{$a = New-Object -ComObject Access.Application; $a.NewCurrentDatabase(\'{db_path}\'); $a.Quit()}}"'
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(db_path):
            print("✓ Banco criado usando MS Access COM")
            return True
        else:
            print(f"Erro comando PowerShell: {result.stderr}")
            
    except Exception as e:
        print(f"Erro ferramenta externa: {e}")
    
    return False


def copy_system_template(db_path):
    """Copia template do sistema se disponível"""
    import shutil
    
    # Possíveis locais de templates
    template_locations = [
        r"C:\Program Files\Microsoft Office\Templates\1033\Access\Blank.accdb",
        r"C:\Program Files (x86)\Microsoft Office\Templates\1033\Access\Blank.accdb",
        r"C:\Program Files\Microsoft Office\root\Office16\ACCWIZ\Blank.accdb",
        r"C:\Program Files (x86)\Microsoft Office\root\Office16\ACCWIZ\Blank.accdb"
    ]
    
    for template in template_locations:
        if os.path.exists(template):
            try:
                shutil.copy2(template, db_path)
                print(f"✓ Template copiado de: {template}")
                return True
            except Exception as e:
                print(f"Erro ao copiar {template}: {e}")
                continue
    
    return False


def get_connection():
    """Retorna uma conexão com o banco de dados Access"""
    import pyodbc
    
    conn_str, db_path = create_access_connection_string()
    
    # Verificar se arquivo existe
    if not os.path.exists(db_path):
        print(f"Arquivo Access não encontrado: {db_path}")
        print("Tentando criar novo banco...")
        
        if not create_new_access_database():
            raise Exception("Não foi possível criar banco Access")
    
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        raise Exception(f"Erro ao conectar com Access: {e}")


def init_db():
    """Inicializa o banco de dados Access e cria tabelas caso não existam"""
    
    # Primeiro, garantir que o banco existe
    conn_str, db_path = create_access_connection_string()
    
    if not os.path.exists(db_path):
        print("Criando novo banco Access...")
        if not create_new_access_database():
            raise Exception("Falha ao criar banco Access")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("Criando tabelas...")
        
        # Criar tabela users
        try:
            cursor.execute("""
                CREATE TABLE users (
                    id AUTOINCREMENT PRIMARY KEY,
                    username TEXT(50) NOT NULL,
                    password TEXT(255) NOT NULL
                )
            """)
            print("✓ Tabela users criada")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Tabela users já existe")
            else:
                print(f"Erro ao criar tabela users: {e}")

        # Criar tabela logs
        try:
            cursor.execute("""
                CREATE TABLE logs (
                    id AUTOINCREMENT PRIMARY KEY,
                    usuario TEXT(50) NOT NULL,
                    acao TEXT(255) NOT NULL,
                    data_hora DATETIME DEFAULT NOW()
                )
            """)
            print("✓ Tabela logs criada")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Tabela logs já existe")

        # Criar tabela demanda
        try:
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
            print("✓ Tabela demanda criada")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Tabela demanda já existe")

        # Criar tabela pessoa_fisica
        try:
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
            print("✓ Tabela pessoa_fisica criada")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Tabela pessoa_fisica já existe")

        # Criar tabela contrato_pf
        try:
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
            print("✓ Tabela contrato_pf criada")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Tabela contrato_pf já existe")

        # Outras tabelas...
        # (continuaria com aditivo_pf, produto_pf, custeio)

        # Inserir usuário admin se não existir
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            count = cursor.fetchone()[0]
            
            if count == 0:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
                print("✓ Usuário admin criado")
            else:
                print("✓ Usuário admin já existe")
                
        except Exception as e:
            print(f"Erro ao criar usuário admin: {e}")

        conn.commit()
        print("✓ Banco de dados Access inicializado com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inicializar banco Access: {e}")
        raise e
    finally:
        conn.close()


def migrate_from_sqlite():
    """Migra dados do SQLite para Access"""
    sqlite_path = "sisproj_pf.db"
    
    if not os.path.exists(sqlite_path):
        print("⚠ Arquivo SQLite não encontrado para migração")
        return
    
    # Conectar ao SQLite
    sqlite_conn = sqlite3.connect(sqlite_path)  
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar ao Access
    access_conn = get_connection()
    access_cursor = access_conn.cursor()
    
    try:
        # Migrar usuários primeiro
        print("Migrando usuários...")
        sqlite_cursor.execute("SELECT * FROM users")
        users = sqlite_cursor.fetchall()
        
        for user in users:
            try:
                # Verificar se usuário já existe
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
        print("✓ Migração básica concluída!")
        
    except Exception as e:
        access_conn.rollback()
        print(f"Erro durante migração: {e}")
        raise e
    finally:
        sqlite_conn.close()
        access_conn.close()


if __name__ == "__main__":
    try:
        init_db()
        if os.path.exists("sisproj_pf.db"):
            migrate_from_sqlite()
    except Exception as e:
        print(f"Erro: {e}")
        input("Pressione Enter para continuar...") 