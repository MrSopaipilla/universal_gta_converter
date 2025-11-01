"""
Script para arreglar problemas de codificación en archivos Python
Convierte todos los archivos .py a UTF-8 de forma segura
"""

import os
import shutil
from pathlib import Path

def fix_file_encoding(filepath):
    """Arreglar codificación de un archivo específico"""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'cp850']
    
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Reescribir en UTF-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fijo codificación: {filepath} (era {encoding})")
            return True
            
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            print(f"❌ Error procesando {filepath}: {e}")
            return False
    
    print(f"⚠️ No se pudo leer: {filepath}")
    return False

def fix_all_python_files():
    """Arreglar codificación de todos los archivos .py en el directorio actual y subdirectorios"""
    current_dir = Path(__file__).parent
    
    python_files = []
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.py') and file != 'encoding_fixer.py':
                python_files.append(os.path.join(root, file))
    
    print(f"Encontrados {len(python_files)} archivos Python")
    
    fixed_count = 0
    for filepath in python_files:
        if fix_file_encoding(filepath):
            fixed_count += 1
    
    print(f"✅ Archivos procesados: {fixed_count}/{len(python_files)}")

if __name__ == "__main__":
    fix_all_python_files()
