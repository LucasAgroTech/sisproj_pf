import os
from models.db_manager_access import init_db, migrate_from_sqlite

if __name__ == "__main__":
    print("Inicializando banco de dados Access...")
    init_db()
    
    if os.path.exists("sisproj_pf.db"):
        print("Migrando dados do SQLite para o Access...")
        migrate_from_sqlite()
        print("Migração concluída!")
    else:
        print("Arquivo SQLite não encontrado. Apenas as tabelas foram criadas no Access.")
    
    print("Processo finalizado!") 