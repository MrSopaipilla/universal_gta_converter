import os

def fix_imports():
    """Fix incorrect imports in the codebase"""
    files_to_fix = [
        'operators/conversion.py',
        'external_pose_caller.py',
        'converter.py'
    ]
    
    base_dir = os.path.dirname(__file__)
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        if not os.path.exists(full_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
            
        print(f"📝 Procesando: {file_path}")
        
        # Leer el archivo
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar las importaciones
        if 'operators/' in file_path:
            old = 'from ..gta_conversion_utils_fixed import'
            new = 'from ..gta_conversion_utils import'
        else:
            old = 'from .gta_conversion_utils_fixed import'
            new = 'from .gta_conversion_utils import'
            
        # Hacer el reemplazo
        new_content = content.replace(old, new)
        
        # Guardar cambios
        if new_content != content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Importaciones corregidas en: {file_path}")
        else:
            print(f"ℹ️ No se requirieron cambios en: {file_path}")

if __name__ == '__main__':
    fix_imports()
