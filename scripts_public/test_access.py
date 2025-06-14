import os
import pyodbc

# Obtém o caminho absoluto do banco
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "sisproj_pf.accdb"))

print(f"Caminho do banco: {db_path}")
print(f"O arquivo existe? {os.path.exists(db_path)}")

# Lista drivers ODBC disponíveis
print("\nDrivers ODBC disponíveis:")
for driver in pyodbc.drivers():
    print(f"- {driver}")

# Tenta conexão
if not os.path.exists(db_path):
    print("\nCriando arquivo vazio do Access...")
    import win32com.client
    access = win32com.client.Dispatch("Access.Application")
    access.NewCurrentDatabase(db_path)
    access.Quit()
    print(f"Arquivo criado em: {db_path}")

print("\nTentando conexão...")
conn_str = (
    f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};"
    f"DBQ={db_path};"
)
try:
    conn = pyodbc.connect(conn_str)
    print("Conexão bem sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro na conexão: {e}") 