#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpiador de carpetas __pycache__
Elimina todas las carpetas __pycache__ y sus archivos .pyc/.pyo
en el directorio actual y todos sus subdirectorios.

by YoshiMaincra
"""

import os
import shutil
import sys
from pathlib import Path


def limpiar_pycache(directorio_raiz=None):
    """
    Elimina todas las carpetas __pycache__ encontradas en el directorio
    especificado y todos sus subdirectorios.
    
    Args:
        directorio_raiz (str): Directorio desde donde iniciar la búsqueda.
                              Si es None, usa el directorio actual.
    """
    if directorio_raiz is None:
        directorio_raiz = os.getcwd()
    
    directorio_raiz = Path(directorio_raiz)
    
    if not directorio_raiz.exists():
        print(f"Error: El directorio '{directorio_raiz}' no existe.")
        return
    
    print(f"Buscando carpetas __pycache__ en: {directorio_raiz}")
    print("-" * 60)
    
    carpetas_eliminadas = 0
    archivos_eliminados = 0
    
    # Buscar carpetas __pycache__ recursivamente
    for pycache_dir in directorio_raiz.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                # Contar archivos antes de eliminar
                archivos_en_carpeta = len(list(pycache_dir.iterdir()))
                
                # Eliminar la carpeta y todo su contenido
                shutil.rmtree(pycache_dir)
                
                print(f"✓ Eliminada: {pycache_dir}")
                print(f"  └─ {archivos_en_carpeta} archivos eliminados")
                
                carpetas_eliminadas += 1
                archivos_eliminados += archivos_en_carpeta
                
            except PermissionError:
                print(f"✗ Error de permisos: {pycache_dir}")
            except Exception as e:
                print(f"✗ Error eliminando {pycache_dir}: {e}")
    
    # También buscar archivos .pyc y .pyo sueltos
    extensiones_pyc = ["*.pyc", "*.pyo"]
    archivos_pyc_sueltos = 0
    
    for extension in extensiones_pyc:
        for archivo_pyc in directorio_raiz.rglob(extension):
            try:
                archivo_pyc.unlink()
                print(f"✓ Archivo eliminado: {archivo_pyc}")
                archivos_pyc_sueltos += 1
            except PermissionError:
                print(f"✗ Error de permisos: {archivo_pyc}")
            except Exception as e:
                print(f"✗ Error eliminando {archivo_pyc}: {e}")
    
    # Resumen
    print("-" * 60)
    print(f"Resumen de limpieza:")
    print(f"  • Carpetas __pycache__ eliminadas: {carpetas_eliminadas}")
    print(f"  • Archivos en carpetas __pycache__: {archivos_eliminados}")
    print(f"  • Archivos .pyc/.pyo sueltos: {archivos_pyc_sueltos}")
    print(f"  • Total archivos eliminados: {archivos_eliminados + archivos_pyc_sueltos}")
    
    if carpetas_eliminadas == 0 and archivos_pyc_sueltos == 0:
        print("✓ No se encontraron archivos de cache para eliminar.")


def main():
    """
    Función principal que maneja argumentos de línea de comandos.
    """
    print("=" * 60)
    print("     LIMPIADOR DE CARPETAS __pycache__")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        # Si se proporciona un directorio como argumento
        directorio = sys.argv[1]
        if os.path.exists(directorio):
            limpiar_pycache(directorio)
        else:
            print(f"Error: El directorio '{directorio}' no existe.")
            print("Uso: python limpiar_pycache.py [directorio]")
            sys.exit(1)
    else:
        # Si no se proporciona directorio, usar el actual
        print("No se especificó directorio. Usando directorio actual...")
        limpiar_pycache()
    
    print("\n¡Limpieza completada!")
    
    # Pausa para que el usuario pueda ver los resultados en Windows
    if os.name == 'nt':  # Windows
        input("\nPresiona Enter para salir...")


if __name__ == "__main__":
    main()