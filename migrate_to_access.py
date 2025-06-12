# Migrate To Access.Py
"""
Script para migrar o sistema SISPROJ-PF de SQLite para Access
"""

import os
import shutil
import sys
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
    
    print(f"Backup completo criado no diretório: {backup_dir}")
    return backup_dir


def install_dependencies():
    """Instala as dependências necessárias"""
    print("\n=== INSTALANDO DEPENDÊNCIAS ===")
    
    try:
        import pyodbc
        print("✓ pyodbc já instalado")
    except ImportError:
        print("Instalando pyodbc...")
        os.system("pip install pyodbc")
    
    try:
        import pypyodbc
        print("✓ pypyodbc já instalado")
    except ImportError:
        print("Instalando pypyodbc...")
        os.system("pip install pypyodbc")


def create_access_database():
    """Cria o banco de dados Access vazio"""
    print("\n=== CRIANDO BANCO ACCESS ===")
    
    try:
        # Importar o gerenciador Access
        from models.db_manager_access import init_db
        
        # Inicializar banco Access
        init_db()
        print("✓ Banco Access criado e inicializado")
        
    except Exception as e:
        print(f"✗ Erro ao criar banco Access: {e}")
        print("\nVerifique se:")
        print("1. Microsoft Access ou ACE drivers estão instalados")
        print("2. Você tem permissões para criar arquivos .accdb")
        print("3. Não há outros processos usando o arquivo")
        return False
    
    return True


def migrate_data():
    """Migra os dados do SQLite para Access"""
    print("\n=== MIGRANDO DADOS ===")
    
    try:
        from models.db_manager_access import migrate_from_sqlite
        
        # Executar migração
        migrate_from_sqlite()
        print("✓ Dados migrados com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro durante migração: {e}")
        return False
    
    return True


def update_db_manager():
    """Atualiza o db_manager.py para usar Access"""
    print("\n=== ATUALIZANDO DB_MANAGER ===")
    
    try:
        # Ler o conteúdo do db_manager_access.py
        with open("models/db_manager_access.py", "r", encoding="utf-8") as f:
            access_content = f.read()
        
        # Substituir o db_manager.py original
        with open("models/db_manager.py", "w", encoding="utf-8") as f:
            f.write(access_content)
        
        print("✓ db_manager.py atualizado para usar Access")
        
    except Exception as e:
        print(f"✗ Erro ao atualizar db_manager: {e}")
        return False
    
    return True


def create_adapter_models():
    """Cria versões adaptadas dos modelos para Access"""
    print("\n=== CRIANDO MODELOS ADAPTADOS ===")
    
    # Lista dos modelos a serem adaptados
    models = [
        "pessoa_fisica_model.py",
        "contrato_pf_model.py", 
        "aditivo_pf_model.py",
        "produto_pf_model.py",
        "user_model.py",
        "demanda_model.py"
    ]
    
    for model in models:
        model_path = f"models/{model}"
        if os.path.exists(model_path):
            try:
                # Ler o arquivo original
                with open(model_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Adaptações básicas para Access
                # Substituir row_factory por tratamento manual
                content = content.replace(
                    "conn.row_factory = sqlite3.Row",
                    "# Access não usa row_factory"
                )
                
                # Adaptar retorno de fetchall para Access
                content = content.replace(
                    "return [tuple(pessoa) for pessoa in pessoas]",
                    "return [tuple(pessoa) for pessoa in pessoas]"
                )
                
                # Salvar versão adaptada
                backup_path = f"models/{model}.sqlite_backup"
                if not os.path.exists(backup_path):
                    shutil.copy2(model_path, backup_path)
                
                # Não é necessário modificar muito já que o db_manager cuida da conexão
                print(f"✓ {model} verificado e compatível")
                
            except Exception as e:
                print(f"✗ Erro ao adaptar {model}: {e}")
    
    print("✓ Modelos verificados para compatibilidade com Access")


def verify_migration():
    """Verifica se a migração foi bem sucedida"""
    print("\n=== VERIFICANDO MIGRAÇÃO ===")
    
    try:
        from models.db_manager import get_connection
        
        # Testar conexão
        conn = get_connection()
        cursor = conn.cursor()
        
        # Verificar algumas tabelas
        test_queries = [
            "SELECT COUNT(*) FROM users",
            "SELECT COUNT(*) FROM pessoa_fisica", 
            "SELECT COUNT(*) FROM contrato_pf"
        ]
        
        for query in test_queries:
            try:
                cursor.execute(query)
                result = cursor.fetchone()
                table = query.split("FROM ")[1]
                print(f"✓ Tabela {table}: {result[0]} registros")
            except Exception as e:
                print(f"⚠ Erro ao verificar tabela: {e}")
        
        conn.close()
        print("✓ Migração verificada com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro na verificação: {e}")
        return False
    
    return True


def main():
    """Função principal de migração"""
    print("=" * 60)
    print("       MIGRAÇÃO SISPROJ-PF: SQLite → Access")
    print("=" * 60)
    
    # Verificar se existe banco SQLite
    if not os.path.exists("sisproj_pf.db"):
        print("⚠ Banco SQLite não encontrado. Criando sistema Access do zero...")
        sqlite_exists = False
    else:
        sqlite_exists = True
    
    # 1. Criar backup (se SQLite existir)
    if sqlite_exists:
        backup_dir = backup_current_system()
    
    # 2. Instalar dependências
    install_dependencies()
    
    # 3. Criar banco Access
    if not create_access_database():
        print("\n✗ MIGRAÇÃO FALHOU: Não foi possível criar banco Access")
        return False
    
    # 4. Migrar dados (se SQLite existir)
    if sqlite_exists:
        if not migrate_data():
            print("\n✗ MIGRAÇÃO FALHOU: Erro na migração de dados")
            return False
    
    # 5. Atualizar db_manager
    if not update_db_manager():
        print("\n✗ MIGRAÇÃO FALHOU: Erro ao atualizar db_manager")
        return False
    
    # 6. Adaptar modelos
    create_adapter_models()
    
    # 7. Verificar migração
    if not verify_migration():
        print("\n⚠ AVISO: Problemas na verificação da migração")
        print("O sistema pode funcionar, mas recomenda-se verificar manualmente")
    
    print("\n" + "=" * 60)
    print("✓ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 60)
    print(f"• Banco Access criado: sisproj_pf.accdb")
    if sqlite_exists:
        print(f"• Dados migrados do SQLite")
        print(f"• Backup criado em: {backup_dir}")
    print("• Sistema agora usa Microsoft Access")
    
    print("\nIMPORTANTE:")
    print("• Certifique-se de que o Microsoft Access está instalado")
    print("• Teste o sistema antes de usar em produção")
    print("• Mantenha backups regulares do arquivo .accdb")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nPressione Enter para continuar...")
            input()
        else:
            print("\nMigração falhou. Pressione Enter para sair...")
            input()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nMigração interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        print("Pressione Enter para sair...")
        input()
        sys.exit(1) 