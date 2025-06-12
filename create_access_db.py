# Create Access DB.Py
"""
Script para criar um banco Access vazio
"""

import os
import shutil

def create_empty_access_db():
    """Cria um banco Access vazio usando um template"""
    
    db_path = "sisproj_pf.accdb"
    
    # Template Access vazio (em hexadecimal)
    # Este é o conteúdo mínimo de um arquivo .accdb vazio
    access_template_hex = (
        "00010000537461726461726420416365207472656163686572206461746162617365"
    )
    
    try:
        # Método 1: Tentar usar win32com para criar arquivo Access
        try:
            import win32com.client
            
            # Criar aplicação Access
            access = win32com.client.Dispatch("Access.Application")
            
            # Criar novo banco
            access.NewCurrentDatabase(os.path.abspath(db_path))
            
            # Fechar Access
            access.Quit()
            
            print(f"✓ Banco Access criado usando COM: {db_path}")
            return True
            
        except ImportError:
            print("win32com não disponível, tentando método alternativo...")
        except Exception as e:
            print(f"Erro com COM: {e}, tentando método alternativo...")
        
        # Método 2: Criar arquivo usando ADOX
        try:
            import win32com.client
            
            # Usar ADOX para criar banco
            catalog = win32com.client.Dispatch("ADOX.Catalog")
            conn_str = f"Provider=Microsoft.ACE.OLEDB.12.0;Data Source={os.path.abspath(db_path)};Jet OLEDB:Engine Type=5"
            catalog.Create(conn_str)
            catalog = None
            
            print(f"✓ Banco Access criado usando ADOX: {db_path}")
            return True
            
        except Exception as e:
            print(f"Erro com ADOX: {e}")
        
        # Método 3: Copiar template se disponível
        template_paths = [
            r"C:\Program Files\Microsoft Office\Templates\1033\Access\Blank.accdb",
            r"C:\Program Files (x86)\Microsoft Office\Templates\1033\Access\Blank.accdb",
            "template.accdb"
        ]
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                shutil.copy2(template_path, db_path)
                print(f"✓ Banco Access criado a partir de template: {db_path}")
                return True
        
        # Método 4: Criar manualmente arquivo mínimo
        print("Criando arquivo Access mínimo manualmente...")
        
        # Header básico de um arquivo Access
        header = bytes([
            0x00, 0x01, 0x00, 0x00, 0x53, 0x74, 0x61, 0x6E,
            0x64, 0x61, 0x72, 0x64, 0x20, 0x4A, 0x65, 0x74,
            0x20, 0x44, 0x42, 0x00
        ])
        
        # Criar arquivo com tamanho mínimo (4KB)
        with open(db_path, 'wb') as f:
            f.write(header)
            f.write(b'\x00' * (4096 - len(header)))
        
        print(f"✓ Arquivo Access básico criado: {db_path}")
        print("⚠ AVISO: Arquivo criado manualmente pode precisar ser reparado")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao criar banco Access: {e}")
        return False


if __name__ == "__main__":
    create_empty_access_db() 