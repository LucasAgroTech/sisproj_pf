import os
import sys
import subprocess

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Instala pacotes necessários
print("Instalando pacotes necessários...")
required_packages = ["pywin32"]
for package in required_packages:
    try:
        install_package(package)
    except:
        print(f"Erro ao instalar {package}, mas vamos continuar...")

import win32com.client

# Caminho para o novo banco
db_path = os.path.abspath("sisproj_pf.accdb")

print(f"Tentando criar banco de dados em: {db_path}")

try:
    # Remove arquivo existente se houver
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Arquivo antigo removido.")
    
    # Cria novo banco
    access = win32com.client.Dispatch("Access.Application")
    access.NewCurrentDatabase(db_path)
    access.Quit()
    
    print(f"\nBanco de dados criado com sucesso em: {db_path}")
    print("Agora você pode executar init_access_db.py para criar as tabelas.")
    
except Exception as e:
    print(f"\nErro ao criar banco de dados: {e}")
    print("\nSugestões:")
    print("1. Verifique se o Microsoft Access está instalado")
    print("2. Verifique se você tem permissão para criar arquivos no diretório")
    print("3. Certifique-se de que nenhum outro programa está usando o arquivo") 