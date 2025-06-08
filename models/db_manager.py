# Db Manager.Py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "sisproj_pf.db")


def get_connection():
    """Retorna uma conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn


def fix_modalidade_constraint():
    """Corrige o constraint de modalidade na tabela contrato_pf para aceitar valores em maiúsculo"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar quantos contratos existem
        cursor.execute('SELECT COUNT(*) FROM contrato_pf')
        count = cursor.fetchone()[0]
        print(f'Contratos existentes: {count}')
        
        if count > 0:
            # Backup dos dados existentes
            cursor.execute('''
                CREATE TEMPORARY TABLE contrato_pf_backup AS 
                SELECT * FROM contrato_pf
            ''')
            print('Backup dos contratos criado.')
        
        # Remover a tabela atual
        cursor.execute('DROP TABLE IF EXISTS contrato_pf')
        print('Tabela contrato_pf removida.')
        
        # Recriar a tabela com o constraint correto
        cursor.execute('''
            CREATE TABLE contrato_pf (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_demanda INTEGER,
                id_pessoa_fisica INTEGER,
                instituicao TEXT, 
                instrumento TEXT, 
                subprojeto TEXT, 
                ta TEXT, 
                pta TEXT, 
                acao TEXT,
                resultado TEXT, 
                meta TEXT, 
                modalidade TEXT CHECK(modalidade IN ('BOLSA', 'PRODUTO', 'RPA', 'CLT')),
                natureza_demanda TEXT CHECK(natureza_demanda IN ('novo', 'renovacao')),
                numero_contrato TEXT,
                vigencia_inicial TEXT,
                vigencia_final TEXT,
                meses INTEGER,
                status_contrato TEXT CHECK(status_contrato IN ('pendente_assinatura', 'cancelado', 'concluido', 
                                                             'em_tramitacao', 'aguardando_autorizacao', 'nao_autorizado',
                                                             'rescindido', 'vigente')),
                remuneracao REAL,
                intersticio INTEGER CHECK(intersticio IN (0, 1)),
                valor_intersticio REAL,
                valor_complementar REAL,
                total_contrato REAL,
                observacoes TEXT,
                FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo),
                FOREIGN KEY (id_pessoa_fisica) REFERENCES pessoa_fisica(id)
            )
        ''')
        print('Tabela contrato_pf recriada com constraint correto.')
        
        if count > 0:
            # Restaurar os dados, convertendo modalidades em minúsculo para maiúsculo se necessário
            cursor.execute('''
                INSERT INTO contrato_pf 
                SELECT 
                    id, codigo_demanda, id_pessoa_fisica, instituicao, instrumento, subprojeto, 
                    ta, pta, acao, resultado, meta,
                    CASE 
                        WHEN modalidade = 'bolsa' THEN 'BOLSA'
                        WHEN modalidade = 'produto' THEN 'PRODUTO'
                        ELSE modalidade 
                    END as modalidade,
                    natureza_demanda, numero_contrato, vigencia_inicial, vigencia_final, 
                    meses, status_contrato, remuneracao, intersticio, valor_intersticio, 
                    valor_complementar, total_contrato, observacoes
                FROM contrato_pf_backup
            ''')
            print(f'Dados restaurados ({count} contratos).')
            
            # Remover backup temporário
            cursor.execute('DROP TABLE contrato_pf_backup')
        
        conn.commit()
        print('Constraint de modalidade corrigido com sucesso!')
        return True
        
    except Exception as e:
        print(f'Erro ao corrigir constraint: {e}')
        conn.rollback()
        return False
    finally:
        conn.close()


def init_db():
    """Inicializa o banco de dados e cria tabelas caso não existam"""
    conn = get_connection()
    cursor = conn.cursor()

    # Usuários (usuário inicial: admin/admin)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL -- hashed em produção
    );
    """
    )

    # Verifica se já existe usuário admin
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin")
        )

    # Logs de acesso e ações
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        acao TEXT NOT NULL,
        data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    # Demanda (reutilizada do projeto PJ)
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS demanda (
        codigo INTEGER PRIMARY KEY AUTOINCREMENT,
        data_entrada TEXT,
        solicitante TEXT,
        data_protocolo TEXT,
        oficio TEXT,
        nup_sei TEXT,
        status TEXT
    );
    """
    )

    # Pessoa Física
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS pessoa_fisica (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_completo TEXT NOT NULL,
        cpf TEXT UNIQUE,
        email TEXT,
        telefone TEXT,
        data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """
    )

    # Contrato de Pessoa Física
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS contrato_pf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_demanda INTEGER,
        id_pessoa_fisica INTEGER,
        instituicao TEXT, 
        instrumento TEXT, 
        subprojeto TEXT, 
        ta TEXT, 
        pta TEXT, 
        acao TEXT,
        resultado TEXT, 
        meta TEXT, 
        modalidade TEXT CHECK(modalidade IN ('BOLSA', 'PRODUTO', 'RPA', 'CLT')),
        natureza_demanda TEXT CHECK(natureza_demanda IN ('novo', 'renovacao')),
        numero_contrato TEXT,
        vigencia_inicial TEXT,
        vigencia_final TEXT,
        meses INTEGER,
        status_contrato TEXT CHECK(status_contrato IN ('pendente_assinatura', 'cancelado', 'concluido', 
                                                    'em_tramitacao', 'aguardando_autorizacao', 'nao_autorizado',
                                                    'rescindido', 'vigente')),
        remuneracao REAL,
        intersticio INTEGER CHECK(intersticio IN (0, 1)),
        valor_intersticio REAL,
        valor_complementar REAL,
        total_contrato REAL,
        observacoes TEXT,
        FOREIGN KEY (codigo_demanda) REFERENCES demanda(codigo),
        FOREIGN KEY (id_pessoa_fisica) REFERENCES pessoa_fisica(id)
    );
    """
    )

    # Aditivo de Contrato PF
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS aditivo_pf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_contrato INTEGER,
        tipo_aditivo TEXT CHECK(tipo_aditivo IN ('prorrogacao', 'reajuste', 'ambos', 'tempo', 'valor', 'tempo e valor', 'TEMPO', 'VALOR', 'TEMPO E VALOR')),
        oficio TEXT,
        data_entrada TEXT,
        data_protocolo TEXT,
        instituicao TEXT, 
        instrumento TEXT, 
        subprojeto TEXT, 
        ta TEXT, 
        pta TEXT, 
        acao TEXT,
        resultado TEXT, 
        meta TEXT,
        vigencia_final TEXT,
        meses INTEGER,
        valor_aditivo REAL,
        vigencia_inicial TEXT,
        nova_remuneracao REAL,
        diferenca_remuneracao REAL,
        valor_complementar REAL,
        valor_total_aditivo REAL,
        responsavel TEXT,
        data_atualizacao TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_contrato) REFERENCES contrato_pf(id)
    );
    """
    )

    # Produtos para contrato PF
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS produto_pf (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_contrato INTEGER,
        numero TEXT,
        data_programada TEXT,
        instrumento TEXT,
        data_entrega TEXT,
        status TEXT CHECK(status IN ('programado', 'em_execucao', 'entregue', 'cancelado')),
        titulo TEXT,
        valor REAL,
        FOREIGN KEY (id_contrato) REFERENCES contrato_pf(id)
    );
    """
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
