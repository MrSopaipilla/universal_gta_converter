#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar la estructura del proyecto
Equivalente al archivo print_structure.bat
"""

import os
import sys
from pathlib import Path

def print_directory_structure():
    """Imprime la estructura del directorio actual"""
    
    # Obtener la ruta del script
    script_path = Path(__file__).parent.absolute()
    
    print("=" * 39)
    print("   ESTRUCTURA DEL PROYECTO")
    print("=" * 39)
    print()
    print(f"Ruta: {script_path}")
    print()
    
    # Mostrar contenido de la carpeta (equivalente a dir /b)
    print("Contenido de la carpeta:")
    print()
    
    try:
        items = sorted(os.listdir(script_path))
        for item in items:
            print(item)
    except PermissionError:
        print("Error: No se tienen permisos para leer la carpeta")
        return
    except FileNotFoundError:
        print("Error: Carpeta no encontrada")
        return
    
    print()
    
    # Mostrar estructura tipo tree
    print("Estructura con tree:")
    print_tree_structure(script_path)
    print()

def print_tree_structure(path, prefix="", max_depth=3, current_depth=0):
    """
    Imprime la estructura de directorios en formato tree
    
    Args:
        path: Ruta a mostrar
        prefix: Prefijo para la indentación
        max_depth: Profundidad máxima a mostrar
        current_depth: Profundidad actual
    """
    if current_depth > max_depth:
        return
    
    try:
        items = sorted(Path(path).iterdir())
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            # Símbolos para el tree
            if is_last:
                current_prefix = "└── "
                next_prefix = prefix + "    "
            else:
                current_prefix = "├── "
                next_prefix = prefix + "│   "
            
            print(f"{prefix}{current_prefix}{item.name}")
            
            # Si es directorio, mostrar su contenido recursivamente
            if item.is_dir() and current_depth < max_depth:
                print_tree_structure(item, next_prefix, max_depth, current_depth + 1)
                
    except PermissionError:
        print(f"{prefix}└── [Acceso denegado]")

def main():
    """Función principal"""
    try:
        print_directory_structure()
        
        # Equivalente al pause del .bat
        input("Presiona Enter para continuar...")
        
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
